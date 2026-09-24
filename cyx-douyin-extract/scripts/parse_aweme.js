/**
 * 解析抖音 aweme_detail.json，输出可读文本
 *
 * 用法:
 *   node parse_aweme.js <aweme_detail.json> [输出txt路径]
 *
 * 不传输出路径则打印到 stdout。
 *
 * 重点: recommend_chapter_info.recommend_chapter_list[].points[].detail
 *       是视频讲解的逐条全文，DOM 里拿不到，只有这个接口有。
 */

const fs = require('fs');

const input = process.argv[2];
const outPath = process.argv[3];
if (!input) { console.error('usage: node parse_aweme.js <aweme_detail.json> [out.txt]'); process.exit(1); }

const j = JSON.parse(fs.readFileSync(input, 'utf8'));
const d = j.aweme_detail || j;
const out = [];
const L = s => out.push(s);
const ts = ms => {
  const s = Math.floor(ms / 1000);
  return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
};

// ---- 基本信息 ----
L('=== 基本信息 ===');
L('标题文案: ' + d.desc);
L('作者: ' + (d.author ? d.author.nickname : '?'));
L('作者简介: ' + (d.author ? (d.author.signature || '').replace(/\n/g, ' / ') : ''));
L('发布时间: ' + new Date(d.create_time * 1000).toISOString());
L('时长: ' + ts(d.duration) + ' (' + d.duration + 'ms)');
L('视频ID: ' + d.aweme_id);

// ---- 互动数据 ----
const st = d.statistics || {};
L('');
L('=== 互动数据 ===');
L('点赞 ' + (st.digg_count || 0) + ' / 评论 ' + (st.comment_count || 0) +
  ' / 收藏 ' + (st.collect_count || 0) + ' / 分享 ' + (st.share_count || 0) +
  ' / 推荐 ' + (st.recommend_count || 0));

// ---- 话题标签 ----
if (Array.isArray(d.text_extra)) {
  const tags = d.text_extra.filter(t => t.hashtag_name).map(t => '#' + t.hashtag_name);
  if (tags.length) { L(''); L('=== 话题标签 ==='); L(tags.join(' ')); }
}

// ---- 章节要点 ★核心 ----
const ci = d.recommend_chapter_info;
if (ci) {
  L('');
  L('=== 内容总述 ===');
  L(ci.chapter_abstract || '(无)');

  L('');
  L('=== 章节逐条讲解 ===');
  (ci.recommend_chapter_list || []).forEach((c, i) => {
    L('');
    L(`--- [${i + 1}] ${c.desc}  (${ts(c.timestamp || 0)}) ---`);
    if (c.detail) L('  ' + c.detail.replace(/\n/g, '\n  '));
    (c.points || []).forEach((p, k) => {
      L(`  · 要点${k + 1}: ${p.desc}`);
      if (p.detail) L('    ' + p.detail.replace(/\n/g, '\n    '));
    });
  });
} else {
  L('');
  L('=== 章节要点 ===');
  L('(该视频无 recommend_chapter_info —— 可能是短视频/无 AI 摘要)');
}

const text = out.join('\n');
if (outPath) { fs.writeFileSync(outPath, text, 'utf8'); console.log('written ' + outPath); }
else console.log(text);
