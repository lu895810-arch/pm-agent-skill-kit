#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cyx-research-report 模板一致性校验。

改动 assets/template.html、cyx-html-style/assets/cyx-html-style.css、SKILL.md 之后跑一次，
确认「速查提到的组件 ↔ 模板 CSS ↔ 模板正文示例」三方对齐，且模板自身不违反硬规则。

用法：
    python scripts/check-template.py

退出码：0 = 全过；1 = 有问题（逐条打印）。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = lambda *a: os.path.join(ROOT, *a)

TEMPLATE = p('assets', 'template.html')
CSS2 = p('cyx-html-style', 'assets', 'cyx-html-style.css')
SKILLS = [p('SKILL.md'), p('cyx-html-style', 'SKILL.md')]

fails = []


def check(name, cond, detail=''):
    mark = 'OK  ' if cond else 'FAIL'
    print('  [%s] %s%s' % (mark, name, ('  → ' + detail) if detail else ''))
    if not cond:
        fails.append(name)


html = io.open(TEMPLATE, encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
# 说明注释里会列出反例词（如「一句话」「机制推演」），检查正文前先剥掉，避免误判
body = re.sub(r'<!--.*?-->', '', html[html.find('</style>'):], flags=re.S)
css2 = io.open(CSS2, encoding='utf-8').read()

print('\n=== 1. 样式与结构 ===')
check('template CSS 花括号平衡', style.count('{') == style.count('}'),
      '%d / %d' % (style.count('{'), style.count('}')))
check('cyx-html-style.css 花括号平衡', css2.count('{') == css2.count('}'),
      '%d / %d' % (css2.count('{'), css2.count('}')))
for tag in ['div', 'section', 'nav', 'main', 'ul', 'li', 'table', 'p', 'span', 'footer']:
    o = len(re.findall(r'<%s[ >]' % tag, html))
    c = html.count('</%s>' % tag)
    check('标签配对 <%s>' % tag, o == c, '%d / %d' % (o, c))

print('\n=== 2. 顶栏导航 ===')
ids = set(re.findall(r'\bid="([^"]+)"', html))
navs = re.findall(r'<a href="#([^"]+)">([^<]+)</a>', html)
nummed = [t for _, t in navs if re.match(r'^\s*\d', t)]
check('nav 项不带序号', not nummed, '带序号: %s' % nummed if nummed else '')
dead = [a for a, _ in navs if a not in ids]
check('nav 锚点都能命中 id', not dead, '死锚点: %s' % dead if dead else '')
check('nav 首位是摘要 / 总览', navs and navs[0][1].strip() in ('摘要', '总览'),
      '首位: %s' % (navs[0][1] if navs else '无'))

print('\n=== 3. 组件三方对齐（速查 ↔ CSS ↔ 正文示例）===')
defined = set(re.findall(r'\.([A-Za-z][-\w]*)', style))
used = set()
for m in re.finditer(r'class="([^"]+)"', body):
    used.update(m.group(1).split())
css2_cls = set(re.findall(r'\.([A-Za-z][-\w]*)', css2))


def refs(path):
    """提取 SKILL.md 里反引号中的 CSS 类名。

    方法调用（`.save(`、`.add_html_to_document(`）与叙述性占位（`1.x`）不是类名，跳过。
    """
    s = io.open(path, encoding='utf-8').read()
    out = set()
    for m in re.finditer(r'`([^`]+)`', s):
        seg = m.group(1)
        for c in re.finditer(r'\.([a-z][a-z0-9-]*)', seg):
            if seg[c.end():c.end() + 1] in ('(', '_'):
                continue
            out.add(c.group(1))
    return out


allref = set()
for f in SKILLS:
    allref |= refs(f)
# 文件后缀与叙述占位（`1.x`）不是类名
allref -= {'md', 'html', 'docx', 'css', 'py', 'js', 'x', 'json', 'yaml'}

miss_css = sorted(c for c in allref if c not in defined)
check('速查提到的类在模板 CSS 中有定义', not miss_css, '缺: %s' % miss_css if miss_css else '')
no_example = sorted(c for c in defined if c not in used)
check('模板 CSS 每个类都有正文示例', not no_example, '无示例: %s' % no_example if no_example else '')
only_t = sorted(defined - css2_cls)
only_c = sorted(css2_cls - defined)
check('模板 CSS 与 cyx-html-style.css 同步', not only_t and not only_c,
      ('仅模板有: %s / 仅 cyx-html-style 有: %s' % (only_t, only_c)) if (only_t or only_c) else '')

print('\n=== 4. 脚注编号 ===')
sup_seq = [int(n) for n in re.findall(r'sup class="fn">(\d+)<', html)]
first_appear = []
for n in sup_seq:
    if n not in first_appear:
        first_appear.append(n)
check('角标编号首现严格递增', first_appear == list(range(1, len(first_appear) + 1)),
      '首现序列: %s' % first_appear)
defined_fn = sorted({int(n) for n in re.findall(r'class="fn-n">(\d+)<', html)})
orphan = sorted(set(sup_seq) - set(defined_fn))
check('每个角标都有对应脚注条目', not orphan, '无条目: %s' % orphan if orphan else '')

print('\n=== 5. 硬规则 ===')
banned = ['一句话', '核心要点', '核心观点', '核心结论', '解读：', '干货', '硬核', '保姆级']
# 只查「被当作标签用」的情形（文本节点开头 / 冒号收尾），句中正常使用（如「核心结论须有 ① 级来源支撑」）不算违规
label_hit = [w for w in banned if re.search(r'>\s*%s|%s[：:]' % (re.escape(w), re.escape(w)), body)]
check('正文无空标签 / 营销词（标签位）', not label_hit, '命中: %s' % label_hit if label_hit else '')
emoji = re.findall(r'[\U0001F300-\U0001FAFF\u26A1\u2705\u2728]', body)
check('正文无 emoji 装点', not emoji, '命中: %s' % emoji if emoji else '')
read_labels = ['机制推演', '路径推演', '逻辑梳理', '推导过程', '速读', '洞察']
hit2 = [w for w in read_labels if w in body]
check('无读法 / 修辞动作标签', not hit2, '命中: %s' % hit2 if hit2 else '')

print('\n=== 6. 技能自我进化机制（第十六节 + feedback-log）===')
skill_main = io.open(SKILLS[0], encoding='utf-8').read()
skill_style = io.open(SKILLS[1], encoding='utf-8').read()
check('SKILL.md 含「十六、技能自我进化机制」', '## 十六、技能自我进化机制' in skill_main)
check('SKILL.md 含反馈落点映射表（A–F 六类）',
      all(k in skill_main for k in ['| A | 事实依据与溯源', '| B | 遣词与命名', '| C | 叙事视角与元信息',
                                    '| D | 结构与层次', '| E | 术语与可读性', '| F | 排版与视觉']))
check('SKILL.md 含资产同步表（16.5）', '资产同步（改一处、必须跟着动哪几处）' in skill_main)
check('SKILL.md 自查含「无前置性元描述」', '无前置性元描述' in skill_main)
check('SKILL.md 自查含「修订记录不入报告」', '修订记录不入报告' in skill_main)
check('cyx-html-style 同步含前置性元描述条目', '前置性元描述' in skill_style)
log_path = p('references', 'feedback-log.md')
has_log = os.path.exists(log_path) and os.path.getsize(log_path) > 0
check('references/feedback-log.md 存在且非空', has_log)
if has_log:
    log = io.open(log_path, encoding='utf-8').read()
    check('feedback-log 含分类字典与日志条目',
          '## 分类字典' in log and '## 日志' in log and '| 1 |' in log,
          '字典 %s / 日志 %s / 首条 %s' % ('## 分类字典' in log, '## 日志' in log, '| 1 |' in log))

print('\n=== 7. 段落分层与框架 ===')
check('SKILL.md 含八.19「段落分层与框架」', '### 19. 段落分层与框架' in skill_main)
check('SKILL.md 含「章法三查」', '章法三查' in skill_main)
check('SKILL.md 自查含「段落有骨架」', '段落有骨架' in skill_main)
check('cyx-html-style 同步含段落分层条目', '段落分层' in skill_style)

print('\n=== 8. 双风格 skill（cyx-md-style / cyx-html-style）===')
check('目录 cyx-html-style 存在（旧目录已改名）', os.path.isdir(p('cyx-html-style')))
check('cyx-html-style/SKILL.md 的 name 字段正确', 'name: cyx-html-style' in skill_style)
check('样式表已更名为 cyx-html-style.css', os.path.exists(CSS2))
md_style_path = p('cyx-md-style', 'SKILL.md')
check('cyx-md-style/SKILL.md 存在', os.path.exists(md_style_path))
if os.path.exists(md_style_path):
    md_style = io.open(md_style_path, encoding='utf-8').read()
    check('cyx-md-style 的 name 字段正确', 'name: cyx-md-style' in md_style)
    check('cyx-md-style 含五段骨架与四级章节',
          all(k in md_style for k in ['一、结构骨架：五段式', '二、层级与标记', '三、语言规范',
                                      '四、逻辑与口径', '五、交付前自查清单']))
    check('cyx-md-style 含分档三件套与口径三级标注',
          '分档三件套' in md_style and '访谈确认' in md_style and '厂商自述' in md_style)
    check('cyx-md-style 声明与 cyx-html-style 的分工', 'cyx-html-style' in md_style)
    check('cyx-md-style 自述条目已去审阅提示', 'T未见第三方核验'[1:] not in md_style and '审阅免责语' in md_style)
check('主 SKILL.md 引用了 cyx-md-style', 'cyx-md-style' in skill_main)
check('主 SKILL.md 五含「审阅免责语全文禁用」规则', '审阅免责语全文禁用' in skill_main)
check('主 SKILL.md 正例已去核验提示', 'T未见第三方核验'[1:] not in skill_main)
# 旧名用拼接构造，避免自检脚本自身被字面量命中
OLD = 'cyx-' + 'style'
check('本脚本与两份 SKILL 无遗留旧名裸引用',
      not any(OLD in io.open(f, encoding='utf-8').read()
              for f in [SKILLS[0], SKILLS[1], os.path.abspath(__file__)]))

print('\n=== 9. 三 skill 进化能力（每个 skill 都能自我进化）===')
MD_SKILL = p('cyx-md-style', 'SKILL.md')
HTML_SKILL = p('cyx-html-style', 'SKILL.md')
md_e = io.open(MD_SKILL, encoding='utf-8').read() if os.path.exists(MD_SKILL) else ''
html_e = io.open(HTML_SKILL, encoding='utf-8').read() if os.path.exists(HTML_SKILL) else ''
check('主 SKILL.md 十六节标注为「三个 skill 共用」', '三个 skill 共用' in skill_main)
check('主 SKILL.md 含 16.10「子 skill 的进化责任」', '子 skill 的进化责任' in skill_main)
check('主 SKILL.md 落点表含「主责 skill」列', '| 主责 skill |' in skill_main)
check('cyx-md-style 含「六、自我进化机制」章节', '## 六、自我进化机制' in md_e)
check('cyx-md-style 含内容侧反馈落点表', '内容侧反馈 → 本 skill 落点' in md_e)
check('cyx-md-style 含越界路由 / 落盘纪律 / 留痕校验 / 回退',
      all(k in md_e for k in ['越界处理', '落盘纪律', '留痕与校验', '规则也会过时']))
check('cyx-md-style 引用共享账本与机检脚本',
      'feedback-log.md' in md_e and 'check-template.py' in md_e)
check('cyx-html-style 含「七、自我进化机制」章节', '## 七、自我进化机制' in html_e)
check('cyx-html-style 含视觉侧反馈落点表', '视觉侧反馈 → 本 skill 落点' in html_e)
check('cyx-html-style 含越界路由 / 落盘纪律 / 留痕校验 / 回退',
      all(k in html_e for k in ['越界处理', '落盘纪律', '留痕与校验', '规则也会过时']))
check('cyx-html-style 引用共享账本与机检脚本',
      'feedback-log.md' in html_e and 'check-template.py' in html_e)
if has_log:
    log_e = io.open(log_path, encoding='utf-8').read()
    check('feedback-log 含归属路由表', '## 归属路由' in log_e)
    check('feedback-log 日志含「归属 skill」列', '归属 skill' in log_e)
    check('feedback-log 分类字典含「主责 skill」列', '| 主责 skill |' in log_e)

print('\n=== 10. 结论证据与叙事链 ===')
check('主 SKILL.md 含八.20「结论要有案例证据」', '### 20. 结论要有案例证据' in skill_main)
check('主 SKILL.md 含「宁缺毋造」与「叙事链」',
      '宁缺毋造' in skill_main and '叙事链' in skill_main)
check('主 SKILL.md 红线一含结论证据要求',
      '结论性内容（判断、定性、排名、趋势）同样适用' in skill_main)
check('主 SKILL.md 自查含「结论有案例证据」与「叙事链闭合」',
      '结论有案例证据' in skill_main and '叙事链闭合' in skill_main)
check('cyx-md-style 含「结论必有案例证据」', '结论必有案例证据' in md_e)
check('cyx-md-style 含「宁缺毋造」与「叙事链闭合」',
      '宁缺毋造' in md_e and '叙事链闭合' in md_e)
check('cyx-md-style 自查含「结论有案例证据」', '结论有案例证据' in md_e)
check('cyx-html-style 数据红线含结论案例证据条', '结论性表述同样要有案例证据' in html_e)
check('cyx-html-style 含「叙事链四环」', '叙事链四环' in html_e)
check('cyx-html-style 自查含「结论有案例证据」', '结论有案例证据' in html_e)
if has_log:
    log_10 = io.open(log_path, encoding='utf-8').read()
    check('feedback-log 记录了「案例证据」反馈', '案例证据' in log_10)

print('\n=== 11. 前置现状对照栏（唯一允许的自指栏目）===')
check('主 SKILL.md 含 8.1「前置现状对照栏」', '### 8.1 前置现状对照栏' in skill_main)
check('主 SKILL.md 8.1 含「我方口径括注不进正文」与判断标尺要求',
      '正文不挂「我方口径」' in skill_main and '判断标尺取自本报告' in skill_main)
check('主 SKILL.md 8.1 含「说明性文字一律不进正文」条文',
      '说明性文字一律不进正文' in skill_main and '删掉这句，读者还能不能看懂' in skill_main)
check('主 SKILL.md 8.1 含「行动项不进本栏」与「不编入正文编号序列」',
      '行动项不进本栏' in skill_main and '不编入正文编号序列' in skill_main)
check('主 SKILL.md 自查含「前置现状对照栏按 8.1 写」', '前置现状对照栏按 8.1 写' in skill_main)
check('主 SKILL.md 8.1 含三段式结构与结论三档取值',
      '三段式结构' in skill_main and '对照表的结论列只用三档取值' in skill_main)
check('主 SKILL.md 8.1 含「去 AI 腔」禁用清单', '去 AI 腔' in skill_main and '归结起来是一句话' in skill_main)
check('cyx-md-style 含「前置现状对照栏」约定', '前置现状对照栏' in md_e)
check('主 SKILL.md 8.1 含「每块必须有骨架」与「小结不写整段」',
      '每块必须有骨架' in skill_main and '小结不写整段' in skill_main and '对得上的' in skill_main)
check('cyx-md-style 含「每块必须有骨架」约定', '每块必须有骨架' in md_e)
check('主 SKILL.md 8.1 含「叙述主体是人（我们）」条文',
      '叙述主体是人（我们）' in skill_main and '报告把' in skill_main)
check('主 SKILL.md 8.1 含「汇报者语体」条文（自称我们 / 表格说人话）',
      '汇报者语体' in skill_main and '自称统一用「我们」' in skill_main and '表格说人话' in skill_main)
check('主 SKILL.md 8.1 结论列三档改白话措辞',
      '已经做到' in skill_main and '这次没涉及' in skill_main)
check('主 SKILL.md 8.1 反例表含「报告把」反例行', '| 「报告把 AI 教室的落地形态归成五类」 |' in skill_main)
check('主 SKILL.md 第 10 节人称规则含第零部分例外', '唯一例外**：「第零部分' in skill_main)
# 只看 0.x 骨架代码块：规则正文里会引用「我方现状」作禁用词，全文件匹配会假失败
_sa = md_e.find('\n## 第零部分')  # 带换行前缀，避免命中 ### 小节标题
_sb = md_e.find('```', _sa) if _sa >= 0 else -1
_skel = md_e[_sa:_sb] if (_sa >= 0 and _sb > _sa) else ''
check('cyx-md-style 骨架示例改用汇报者语体',
      '我们这次归成五类' in _skel and '我方' not in _skel and '汇报者语体' in md_e)
check('cyx-md-style 自查项已去掉旧的「我方口径」口径',
      '挂「**我方口径**」' not in md_e and '三档白话取值' in md_e)
check('主 SKILL.md 八.1 含行业术语白话定义条', '行业术语要给白话定义' in skill_main)
check('主 SKILL.md 八.1 含「我方现状不用观察动词」条', '不用观察动词' in skill_main)
check('cyx-md-style 骨架含术语解释与观察动词修正',
      '为什么叫「样板」' in _skel and '还没按 2025 版指南逐条对标' in _skel)
if has_log:
    check('feedback-log 记录了「现状对照」反馈',
          '现状对照' in io.open(log_path, encoding='utf-8').read())

print('\n=== 12. 板块标题与页面卡片对齐（防双重缩进）===')
BANNER_OK = 'max-width:1360px;padding:0;scroll-margin-top:80px;'
BANNER_LINE_OK = 'left:0;right:0;bottom:-18px;height:1px;'
check('.part-banner 不自带左右 gutter（模板）', BANNER_OK in html)
check('.part-banner 不自带左右 gutter（样式表）', BANNER_OK in css2)
check('.part-banner 装饰线与卡片同宽', BANNER_LINE_OK in html and BANNER_LINE_OK in css2)
check('主 SKILL.md 版心节写明 part-banner 不得再加 gutter', '不得再自带左右 gutter' in skill_main)
check('cyx-html-style 组件速查含同一铁律', '不得自带左右 gutter' in html_e)
if has_log:
    check('feedback-log 记录了「标题与卡片对齐」反馈',
          '标题与卡片' in io.open(log_path, encoding='utf-8').read())

print('\n=== 13. 术语标识（阅读辅助）===')
TERM_CSS = '.tag.term{background:rgba(0,245,212,.10);color:var(--cyan);border:1px dashed rgba(0,245,212,.55)}'
check('术语标识 .tag.term 在模板 CSS 有定义', TERM_CSS in html)
check('术语标识 .tag.term 在 cyx-html-style.css 有定义', TERM_CSS in css2)
check('模板正文有 .tag.term 用法示例', 'class="tag term"' in body)
check('cyx-html-style 组件速查含 .tag.term', '.tag.term' in html_e)
check('主 SKILL.md 八.1 含「术语要给标识」条', '术语要给标识' in skill_main)
check('cyx-md-style 骨架含「〔术语〕」标记', '〔术语〕' in _skel)
if has_log:
    check('feedback-log 记录了「术语标识」反馈',
          '术语标识' in io.open(log_path, encoding='utf-8').read())

print()
if fails:
    print('未通过 %d 项：%s' % (len(fails), '；'.join(fails)))
    sys.exit(1)
print('全部通过。')
