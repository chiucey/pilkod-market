#!/usr/bin/env node
'use strict';
/**
 * validate.js — 段式剧本格式体检
 *
 * 用法: node validate.js <script.md> [--strict]
 *   --strict  把 WARN 也算作失败（退出码 1）
 *
 * 退出码: 0 = 无 ERROR；1 = 有 ERROR（或 --strict 下有 WARN）；2 = 用法/读取错误
 * 只校验格式契约，不校验创作质量（可拍性、情绪表达）。
 */

const fs = require('fs');

const ABSTRACT_ADJ = [
  '美丽', '漂亮', '孤独', '史诗', '震撼', '优雅', '宏大', '瑰丽', '壮丽',
  '凄美', '梦幻般', '神秘感', '紧张的', '悲伤的', '温馨的', '浪漫的', '感人',
];

const REQUIRED_BLOCKS = ['场景', '角色', '音乐', '正文'];
const REQUIRED_SUBBLOCKS = ['环境与人物初始状态', '对话', '动作序列', '镜头提示'];
const SCENE_FIELDS = ['类型', '主要物体', '次要物体', '光线', '氛围', '环境音'];

const ERR = 'ERROR';
const WARN = 'WARN';

function die(msg) {
  process.stderr.write(msg + '\n');
  process.exit(2);
}

/** 去掉 markdown 代码围栏，取出剧本正文。
 *  分段各自围栏时会命中多个代码块，必须全部取出拼接——只取第一个会让
 *  多段剧本被截成 S001，然后「校验通过」，这种假通过比报错更危险。 */
function stripFence(text) {
  const blocks = [];
  const re = /```(?:text|markdown|md)?[ \t]*\r?\n([\s\S]*?)```/g;
  let m;
  while ((m = re.exec(text)) !== null) blocks.push(m[1]);
  if (blocks.length === 0) return text;
  if (blocks.length === 1) return blocks[0];
  return blocks.join('\n\n');
}

function countPieces(s, seps) {
  return s.split(seps).filter((p) => p.trim().length > 0).length;
}

function extractNums(s) {
  const m = s.match(/\d+/g);
  return m ? m.map(Number) : [];
}

function validate(text, opts) {
  const issues = [];
  const lines = text.split(/\r?\n/);
  const add = (level, seg, line, msg) => issues.push({ level, seg, line, msg });

  // --- 切段 ---
  const starts = [];
  lines.forEach((l, i) => {
    const m = l.match(/^\s*段号\s*[:：]\s*(S\d+)\s*$/);
    if (m) starts.push({ idx: i, id: m[1] });
  });

  if (starts.length === 0) {
    add(ERR, '-', 0, '没找到任何「段号: S001」格式的行。文件必须由段式段落组成。');
    return issues;
  }

  // 段号格式 + 连续性（全局一次性检查）
  starts.forEach((s, k) => {
    if (!/^S\d{3}$/.test(s.id)) {
      add(ERR, s.id, s.idx + 1, `段号「${s.id}」不是 S + 三位数字格式，应为 S001 / S002 这种。`);
    }
    if (k > 0) {
      const prev = starts[k - 1];
      const pn = Number(prev.id.slice(1));
      const cn = Number(s.id.slice(1));
      if (Number.isFinite(pn) && Number.isFinite(cn)) {
        if (cn === pn) add(ERR, s.id, s.idx + 1, `段号重复：${s.id} 与上一段相同。`);
        else if (cn < pn) add(ERR, s.id, s.idx + 1, `段号倒退：${prev.id} → ${s.id}，必须连续递增。`);
      }
    }
  });

  starts.forEach((s, k) => {
    const segId = s.id;
    const end = k + 1 < starts.length ? starts[k + 1].idx : lines.length;
    const seg = lines.slice(s.idx, end);
    const ln = (i) => s.idx + i + 1; // 段内索引 -> 全文行号

    // --- 时长 ---
    let duration = null;
    for (let i = 1; i < seg.length; i++) {
      const m = seg[i].match(/^\s*时长\s*[:：]\s*(\d+(?:\.\d+)?)\s*秒\s*$/);
      if (m) { duration = Number(m[1]); break; }
    }
    if (duration === null) {
      add(ERR, segId, s.idx + 1, '缺少「时长: N秒」行。');
    } else if (duration < 4 || duration > 15) {
      add(ERR, segId, ln(1), `时长 ${duration} 秒越界。一段只能 4-15 秒，${duration > 15 ? '必须拆段' : '内容太少，合并到相邻段'}。`);
    }

    // --- 区块定位 ---
    const blocks = {};
    seg.forEach((l, i) => {
      const m = l.match(/^\s*\[([^\]]+)\]\s*$/);
      if (m && !blocks[m[1].trim()]) blocks[m[1].trim()] = { start: i, end: i };
    });
    Object.keys(blocks).forEach((name) => {
      const b = blocks[name];
      const next = seg.findIndex((l, i) => i > b.start && /^\s*\[([^\]]+)\]\s*$/.test(l));
      b.end = next === -1 ? seg.length - 1 : next - 1;
    });

    REQUIRED_BLOCKS.concat(REQUIRED_SUBBLOCKS).forEach((name) => {
      if (!blocks[name]) add(ERR, segId, s.idx + 1, `缺少必需区块 [${name}]。`);
    });

    // 区块顺序
    const order = REQUIRED_BLOCKS.concat(REQUIRED_SUBBLOCKS);
    let lastPos = -1, lastName = null;
    order.forEach((name) => {
      if (!blocks[name]) return;
      if (blocks[name].start < lastPos) {
        add(ERR, segId, ln(blocks[name].start), `区块 [${name}] 出现在 [${lastName}] 之前，顺序应为：${order.join(' → ')}。`);
      } else { lastPos = blocks[name].start; lastName = name; }
    });

    // [人物间关系] 写在初始状态里但长得像子块，单独提醒：它是字段，且模板要求写
    if (blocks['环境与人物初始状态']) {
      const b = blocks['环境与人物初始状态'];
      const body = seg.slice(b.start + 1, b.end + 1).join('\n');
      if (!/\[?\s*人物间关系\s*\]?\s*[:：]/.test(body)) {
        add(WARN, segId, ln(b.start), '初始状态里没写「[人物间关系]:」，多角色同框时缺了互动关系，模型会让各人各自朝向镜头。');
      }
    }

    // --- [场景] 档案字段 ---
    if (blocks['场景']) {
      const b = blocks['场景'];
      const body = seg.slice(b.start + 1, b.end + 1);
      const joined = body.join('\n');
      SCENE_FIELDS.forEach((f) => {
        if (!joined.includes(f)) add(ERR, segId, ln(b.start), `场景档案缺少字段「${f}」。`);
      });
      const primary = body.filter((l) => /^\s*\d+\.\s*[（(]/.test(l));
      if (primary.length > 0 && (primary.length < 3 || primary.length > 5)) {
        add(WARN, segId, ln(b.start), `主要物体 ${primary.length} 个，建议 3-5 个。`);
      } else if (primary.length === 0) {
        add(WARN, segId, ln(b.start), '主要物体应写成「1. （位置）物体 - 状态」这样的编号行，当前没识别到。');
      }
      // 次要物体是「对象 + 空格 + 方位词(1-2字) + 冒号」。不能只认单字方位：
      // 「手里 / 身后 / 脚下 / 上方」是中文里最自然的写法，单字正则会把它们全漏掉。
      // 角色行是「- 名字: 描述」，冒号紧跟名字没有空格，所以不会被这里误匹配。
      const secondary = body.filter((l) => /^\s*-\s*\S+\s+\S{1,2}\s*[:：]/.test(l));
      if (secondary.length === 0) {
        add(WARN, segId, ln(b.start), '没识别到次要物体。应写成「- 白猫 背上: 一道伤口」这种以主要物体为参照的挂载行，5-10 个。');
      } else if (secondary.length < 5 || secondary.length > 10) {
        add(WARN, segId, ln(b.start), `次要物体 ${secondary.length} 个，建议 5-10 个。`);
      }
    }

    // --- [角色] 5 要素 ---
    if (blocks['角色']) {
      const b = blocks['角色'];
      const roleLines = [];
      seg.slice(b.start + 1, b.end + 1).forEach((l, i) => { if (/^\s*-\s*\S/.test(l)) roleLines.push({ i, l }); });
      if (roleLines.length === 0) add(ERR, segId, ln(b.start), '[角色] 区块里没有角色条目。');
      roleLines.forEach(({ i, l }) => {
        if (!/[：:]/.test(l)) {
          add(ERR, segId, ln(b.start + 1 + i), `角色条目缺冒号，应为「- 角色名: 基本信息，本段服装状态，情绪，姿势，位置」：${l.trim()}`);
          return;
        }
        const desc = l.slice(l.indexOf(':') + 1).replace(/^.*[：]/, '');
        const parts = countPieces(desc, /[，,]/);
        if (parts < 3) {
          add(WARN, segId, ln(b.start + 1 + i), `角色「${l.trim().slice(2, 12)}…」只分了 ${parts} 个要素段，5 要素（基本信息/服装状态/情绪/姿势/位置）建议用逗号分开写全。`);
        }
      });
      if (roleLines.length > 3) {
        add(WARN, segId, ln(b.start), `同框角色 ${roleLines.length} 个，超过 3 个时每个角色的动作都会被摊薄，考虑拆段。`);
      }
    }

    // --- [音乐] ---
    if (blocks['音乐']) {
      const b = blocks['音乐'];
      const joined = seg.slice(b.start + 1, b.end + 1).join('\n');
      ['风格', '节奏', '情绪'].forEach((f) => {
        if (!new RegExp(f + '\\s*[:：]').test(joined)) add(ERR, segId, ln(b.start), `[音乐] 缺少字段「${f}」。`);
      });
    }

    // --- [对话] ---
    if (blocks['对话']) {
      const b = blocks['对话'];
      const dlines = seg.slice(b.start + 1, b.end + 1).filter((l) => l.trim().length > 0);
      // 无台词段落：整块写「（无台词）」是合法的，不要逼模型编台词
      const isNoDialogue = dlines.length > 0 && dlines.every((l) => /^[（(]\s*无台词\s*[）)]\s*$/.test(l.trim()));
      if (!isNoDialogue) {
        dlines.forEach((l, i) => {
          const m = l.match(/^\s*([^（(:：\s]+)\s*[（(]([^）)]*)[）)]\s*[:：]\s*(.+)$/);
          if (!m) {
            add(ERR, segId, ln(b.start + 1 + i), `对话格式不对，应为「说话人（语气/动作）: 内容」：${l.trim()}`);
          } else if (m[2].trim().length === 0) {
            add(ERR, segId, ln(b.start + 1 + i), `「${m[1]}」的括号是空的，语气和动作至少要有一个，否则模型不知道这句话该怎么说怎么做。`);
          }
        });
      }
    }

    // --- [动作序列] 编号 ---
    let actionMax = 0;
    if (blocks['动作序列']) {
      const b = blocks['动作序列'];
      const alines = [];
      seg.slice(b.start + 1, b.end + 1).forEach((l, i) => { if (/^\s*\d+\s*[.、]/.test(l)) alines.push({ i, l }); });
      alines.forEach(({ i, l }, idx) => {
        const n = Number(l.match(/^\s*(\d+)/)[1]);
        if (n !== idx + 1) {
          add(ERR, segId, ln(b.start + 1 + i), `动作编号不连续：第 ${idx + 1} 条写的是 ${n}。`);
        }
        actionMax = Math.max(actionMax, n);
      });
      if (alines.length > 10) {
        add(WARN, segId, ln(b.start), `本段 ${alines.length} 个动作，超出最多 15 秒能承载的上限（4-8 个），再密视频模型会丢动作。`);
      }
      if (alines.length > 0 && !alines.some(({ l }) => /音效|（[^）]*声[^）]*）/.test(l))) {
        add(WARN, segId, ln(b.start), '关键动作都没有音效标注，音轨会没有切分点。');
      }
    }

    // --- [镜头提示] 动作回指 ---
    if (blocks['镜头提示']) {
      const b = blocks['镜头提示'];
      const clines = [];
      seg.slice(b.start + 1, b.end + 1).forEach((l, i) => { if (/^\s*[-*]?\s*镜头\s*\d+/.test(l)) clines.push({ i, l }); });
      if (clines.length === 0) add(ERR, segId, ln(b.start), '镜头提示为空。');
      clines.forEach(({ i, l }) => {
        const no = ln(b.start + 1 + i);
        const arrow = l.match(/→\s*动作\s*([0-9,\s和、]+)/);
        if (!arrow) {
          add(ERR, segId, no, `镜头缺少「→ 动作 X, Y」回指：${l.trim()}`);
          return;
        }
        const nums = extractNums(arrow[1]);
        if (nums.length === 0) {
          add(ERR, segId, no, `「→ 动作」后面没有动作编号：${l.trim()}`);
        } else {
          nums.forEach((n) => {
            if (actionMax > 0 && n > actionMax) {
              add(ERR, segId, no, `镜头回指动作 ${n}，但本段动作序列只到 ${actionMax}。`);
            }
            if (n < 1) add(ERR, segId, no, `镜头回指动作 ${n}，动作编号从 1 开始。`);
          });
        }
        const head = l.slice(0, l.indexOf('→'));
        const dims = countPieces(head, /[，,、\/]/);
        if (dims < 2) {
          add(WARN, segId, no, `镜头参数只有 ${dims} 项，应写「景别 / 角度 / 运镜」：${l.trim()}`);
        }
      });
    }

    // --- 抽象形容词单独成句 ---
    seg.forEach((l, i) => {
      const t = l.trim().replace(/^[，、,.\s]+|[，、,.\s]+$/g, '');
      if (t.length === 0 || t.length > 8) return;
      if (!ABSTRACT_ADJ.some((w) => t.includes(w))) return;
      if (/[（(]/.test(t)) return;
      if (/^[\d.\s]*[段时镜头-]*$/.test(t)) return;
      // 「氛围: 震撼」这类字段值位置本来就填抽象词，只罚正文里的独立成句
      if (/^\S+\s*[:：]/.test(t)) return;
      add(WARN, segId, ln(i), `「${t}」疑似抽象形容词单独成句，写成具象画面或落到身体动作上。`);
    });
  });

  return { issues, segIds: starts.map((s) => s.id) };
}

function main() {
  const argv = process.argv.slice(2);
  const strict = argv.includes('--strict');
  const file = argv.filter((a) => !a.startsWith('--'))[0];
  if (!file) die('用法: node validate.js <script.md> [--strict]');

  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (e) {
    die(`读不到文件: ${file} (${e.code || e.message})`);
  }

  const text = stripFence(raw);
  const { issues, segIds } = validate(text, { strict });

  const errors = issues.filter((i) => i.level === ERR);
  const warns = issues.filter((i) => i.level === WARN);

  if (issues.length) {
    process.stdout.write(issues.map((i) => `${i.level}  ${i.seg}  L${i.line}  ${i.msg}`).join('\n') + '\n\n');
  }
  process.stdout.write(`检查 ${segIds.length} 段：ERROR ${errors.length} / WARN ${warns.length}\n`);
  if (errors.length === 0 && warns.length === 0) {
    process.stdout.write('格式校验通过。\n');
  }

  process.exit(errors.length > 0 || (strict && warns.length > 0) ? 1 : 0);
}

if (require.main === module) main();

module.exports = { validate, stripFence };
