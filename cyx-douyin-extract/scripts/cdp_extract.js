/**
 * 抖音视频内容提取 —— Edge headless + CDP
 *
 * 用法:
 *   node cdp_extract.js <视频URL或ID> <输出目录>
 *
 * 产出（全部写到输出目录）:
 *   _log.txt             运行日志（PowerShell 不回显 stdout，所以必须写文件）
 *   body.txt             页面 DOM 文本（含评论区、互动数、推荐列表）
 *   aweme_detail.json    视频详情接口原始响应（含章节点讲解全文）★核心
 *   shot.png             页面截图
 *   meta.json            标题 / URL
 *
 * 设计说明:
 *   - 手搓 WebSocket 客户端（Node 原生 net + crypto，RFC6455），不依赖 ws 包
 *   - 独立 user-data-dir，不污染用户真实 Edge 配置
 *   - 必须监听 Network.responseReceived + getResponseBody 才能拿到章节点讲解，
 *     DOM 里只有章节标题
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const net = require('net');
const crypto = require('crypto');
const { spawn } = require('child_process');

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PORT = 9240;

// ---------- 入参 ----------
const arg = process.argv[2] || '';
const OUTDIR = process.argv[3] || process.cwd();
if (!arg) { console.error('need video url or id'); process.exit(1); }

// 从分享链接或裸 ID 里抠出 video id
let videoId = arg;
const m = arg.match(/video\/(\d+)/);
if (m) videoId = m[1];
else {
  const m2 = arg.match(/(\d{15,})/);
  if (m2) videoId = m2[1];
}
const TARGET = 'https://www.douyin.com/video/' + videoId;
// 抓这个接口才有章节点讲解
const DETAIL_API_HINT = 'aweme/detail';

const USER_DIR = path.join(OUTDIR, '_edgeprofile');
const LOG = path.join(OUTDIR, '_log.txt');
fs.mkdirSync(OUTDIR, { recursive: true });
fs.writeFileSync(LOG, 'START ' + TARGET + '\n', 'utf8');
const log = s => fs.appendFileSync(LOG, s + '\n', 'utf8');

const getJSON = url => new Promise((res, rej) => {
  http.get(url, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => { try { res(JSON.parse(d)); } catch (e) { rej(e); } }); }).on('error', rej);
});
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------- 最小 WebSocket 客户端 ----------
class WS {
  constructor(url) {
    const u = new URL(url);
    this.host = u.hostname; this.port = u.port || 80;
    this.path = u.pathname + u.search;
    this.buf = Buffer.alloc(0); this.handlers = [];
  }
  connect() {
    return new Promise((resolve, reject) => {
      const key = crypto.randomBytes(16).toString('base64');
      this.sock = net.connect(this.port, this.host, () => {
        this.sock.write(
          `GET ${this.path} HTTP/1.1\r\nHost: ${this.host}:${this.port}\r\n` +
          `Upgrade: websocket\r\nConnection: Upgrade\r\n` +
          `Sec-WebSocket-Key: ${key}\r\nSec-WebSocket-Version: 13\r\n\r\n`);
      });
      this.sock.on('error', reject);
      let hs = false;
      this.sock.on('data', d => {
        if (!hs) {
          this.buf = Buffer.concat([this.buf, d]);
          const i = this.buf.indexOf('\r\n\r\n');
          if (i >= 0) { hs = true; this.buf = this.buf.slice(i + 4); this._drain(); resolve(); }
          return;
        }
        this.buf = Buffer.concat([this.buf, d]); this._drain();
      });
    });
  }
  _drain() {
    while (true) {
      if (this.buf.length < 2) return;
      const b0 = this.buf[0], b1 = this.buf[1];
      const op = b0 & 0x0f, mk = (b1 & 0x80) !== 0;
      let len = b1 & 0x7f, off = 2;
      if (len === 126) { if (this.buf.length < 4) return; len = this.buf.readUInt16BE(2); off = 4; }
      else if (len === 127) { if (this.buf.length < 10) return; len = Number(this.buf.readBigUInt64BE(2)); off = 10; }
      let key = null;
      if (mk) { if (this.buf.length < off + 4) return; key = this.buf.slice(off, off + 4); off += 4; }
      if (this.buf.length < off + len) return;
      let pl = this.buf.slice(off, off + len);
      if (mk) { const p = Buffer.from(pl); for (let i = 0; i < p.length; i++) p[i] ^= key[i % 4]; pl = p; }
      this.buf = this.buf.slice(off + len);
      if (op === 1 || op === 0) { const t = pl.toString('utf8'); this.handlers.forEach(h => h(t)); }
      else if (op === 8) this.sock.end();
    }
  }
  send(str) {
    const pl = Buffer.from(str, 'utf8'); const len = pl.length;
    const mask = crypto.randomBytes(4); let h;
    if (len < 126) { h = Buffer.alloc(6); h[1] = 0x80 | len; mask.copy(h, 2); }
    else if (len < 65536) { h = Buffer.alloc(8); h[1] = 0x80 | 126; h.writeUInt16BE(len, 2); mask.copy(h, 4); }
    else { h = Buffer.alloc(14); h[1] = 0x80 | 127; h.writeBigUInt64BE(BigInt(len), 2); mask.copy(h, 10); }
    h[0] = 0x81;
    const mp = Buffer.from(pl);
    for (let i = 0; i < mp.length; i++) mp[i] ^= mask[i % 4];
    this.sock.write(Buffer.concat([h, mp]));
  }
  close() { try { this.sock.end(); } catch (e) {} }
}

// ---------- 主流程 ----------
(async () => {
  // 1. 起 Edge
  const edge = spawn(EDGE, [
    '--headless=new', '--disable-gpu', '--mute-audio',
    '--no-first-run', '--no-default-browser-check',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${USER_DIR}`,
    '--window-size=1400,1600',
    'about:blank'
  ], { windowsHide: true, stdio: 'ignore' });
  log('edge pid=' + edge.pid);

  for (let i = 0; i < 60; i++) {
    await sleep(500);
    try { await getJSON(`http://127.0.0.1:${PORT}/json/version`); break; } catch (e) {}
  }
  log('devtools up');

  const list = await getJSON(`http://127.0.0.1:${PORT}/json/list`);
  const page = list.find(t => t.type === 'page');
  const ws = new WS(page.webSocketDebuggerUrl);
  await ws.connect();
  log('ws connected');

  let id = 1; const pend = new Map();
  const detailReqs = [];
  ws.handlers.push(txt => {
    try {
      const o = JSON.parse(txt);
      if (o.id && pend.has(o.id)) { pend.get(o.id)(o); pend.delete(o.id); return; }
      if (o.method === 'Network.responseReceived' && o.params.response.url.includes(DETAIL_API_HINT)) {
        detailReqs.push({ reqId: o.params.requestId, url: o.params.response.url });
      }
    } catch (e) {}
  });
  const cmd = (m, p) => new Promise(r => {
    const i = id++; pend.set(i, r);
    ws.send(JSON.stringify({ id: i, method: m, params: p || {} }));
    setTimeout(() => { if (pend.has(i)) { pend.delete(i); r(null); } }, 40000);
  });

  await cmd('Page.enable');
  await cmd('Runtime.enable');
  await cmd('Network.enable');

  // 2. 导航并等加载
  await cmd('Page.navigate', { url: TARGET });
  for (let i = 0; i < 40; i++) {
    await sleep(1000);
    const r = await cmd('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
    const v = r && r.result && r.result.result ? r.result.result.value : '?';
    if (v === 'complete') { log('loaded at ' + i + 's'); break; }
  }
  await sleep(6000); // 留时间给接口返回

  const ev = async expr => {
    const r = await cmd('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return r && r.result && r.result.result ? r.result.result.value : null;
  };

  // 3. 存 DOM 文本
  const body = await ev('document.body.innerText');
  fs.writeFileSync(path.join(OUTDIR, 'body.txt'), body || '', 'utf8');
  log('body len=' + (body ? body.length : 0));

  const title = await ev('document.title');
  fs.writeFileSync(path.join(OUTDIR, 'meta.json'),
    JSON.stringify({ title, url: TARGET, videoId }, null, 2), 'utf8');

  // 4. 存详情接口响应 ★核心
  log('detail requests=' + detailReqs.length);
  let saved = 0;
  for (const dr of detailReqs) {
    const r = await cmd('Network.getResponseBody', { requestId: dr.reqId });
    if (r && r.result && r.result.body && r.result.body.length > 10000) {
      fs.writeFileSync(path.join(OUTDIR, 'aweme_detail.json'), r.result.body, 'utf8');
      log('saved aweme_detail.json len=' + r.result.body.length);
      saved++;
      if (saved >= 1) break;
    }
  }
  if (!saved) log('WARN: no aweme/detail response captured');

  // 5. 截图
  const shot = await cmd('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  if (shot && shot.result && shot.result.data) {
    fs.writeFileSync(path.join(OUTDIR, 'shot.png'), Buffer.from(shot.result.data, 'base64'));
    log('screenshot ok');
  } else log('screenshot failed');

  ws.close();
  try { edge.kill(); } catch (e) {}
  log('ALL_DONE');
  process.exit(0);
})();
