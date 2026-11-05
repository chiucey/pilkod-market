#!/usr/bin/env node
/**
 * 咪咕微博每日内容抓取 → Excel输出
 * 视频链接格式：https://weibo.com/tv/show/1034:{media_id}
 */

const https = require("https");
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// skill目录使用相对路径，运行时解析为真实路径
const SKILL_DIR = path.dirname(__dirname);
const OUTPUT_DIR = path.join(SKILL_DIR, "data");
const COOKIE_FILE = path.join(SKILL_DIR, "scripts", "weibo_cookies.json");
const EXCEL_GENERATOR = path.join(SKILL_DIR, "scripts", "excel_generator.js");

const ACCOUNTS = [
  ["熊猫", "开饭了大熊猫",     "7012741040"],
  ["熊猫", "熊猫观察君",       "5921248068"],
  ["熊猫", "咪咕Panda",       "7013379023"],
  ["综合", "咪咕",            "5428441557"],
  ["综合", "咪咕音乐",         "1867028705"],
  ["综合", "咪咕娱乐",         "7012740989"],
  ["综合", "咪咕视频",         "1809436135"],
  ["体育", "咪咕奥运",         "6407423563"],
  ["体育", "咪咕冰雪",         "7051979649"],
  ["体育", "咪咕格斗",         "6367852329"],
  ["体育", "咪咕篮球",         "6364463717"],
  ["体育", "咪咕乒乓球",       "6364463720"],
  ["体育", "咪咕斯诺克",       "6407058677"],
  ["体育", "咪咕体育",         "6320391439"],
  ["体育", "跟我一起看足球",   "7308622389"],
  ["体育", "咪咕足球",         "6364463714"],
  ["体育", "体育叨叨酱",       "2154336701"],
  ["体育", "我们都是足球迷",   "6364463702"],
  ["体育", "野生乒乓",         "6367852412"],
  ["体育", "CBA最前沿",        "7331026558"],
  ["体育", "篮球记事本",        "6364463668"],
  ["体育", "UFC终极格斗冠军赛", "5311723972"],
];

function getTimeWindow() {
  const now = new Date();
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  yesterday.setHours(8, 40, 0, 0);
  const today = new Date(now);
  today.setHours(8, 40, 0, 0);
  return {
    startTs: Math.floor(yesterday.getTime() / 1000),
    endTs: Math.floor(today.getTime() / 1000),
    dateStr: yesterday.toISOString().slice(0, 10),
  };
}

function httpGet(hostname, pathStr, cookie) {
  return new Promise((resolve, reject) => {
    const req = https.get({ hostname, path: pathStr, headers: {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
      "Cookie": cookie,
      "X-Requested-With": "XMLHttpRequest",
      "Referer": "https://weibo.com/u/5428441557",
    }}, res => {
      let data = "";
      res.on("data", c => data += c);
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`JSON解析失败: ${e.message}`)); }
      });
    });
    req.on("error", reject);
    req.setTimeout(15000, () => { req.destroy(); reject(new Error("请求超时")); });
  });
}

function cleanText(html) {
  if (!html) return "";
  return html
    .replace(/<a[^>]*>/g, "")
    .replace(/<\/a>/g, "")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&#(\d+);/g, (m, dec) => String.fromCharCode(dec))
    .replace(/\s+/g, " ")
    .trim();
}

function extractVideoUrl(pageInfo) {
  if (!pageInfo) return "";
  const mi = pageInfo.media_info;
  if (!mi) return "";
  if (mi.media_id) return `https://weibo.com/tv/show/1034:${mi.media_id}`;
  if (pageInfo.page_url) return pageInfo.page_url;
  return mi.mp4_hd_url || mi.mp4_sd_url || "";
}

function extractPicUrls(mblog) {
  if (mblog.pic_urls?.length) {
    return mblog.pic_urls.slice(0, 3).map(u => u.replace("\\", "")).join(" | ");
  }
  if (mblog.pic_ids?.length) {
    return mblog.pic_ids.slice(0, 3).map(id => `https://wx4.sinaimg.cn/orj360/${id}.jpg`).join(" | ");
  }
  const rt = mblog.retweeted_status;
  if (rt?.pic_urls?.length) {
    return rt.pic_urls.slice(0, 3).map(u => u.replace("\\", "")).join(" | ");
  }
  if (rt?.pic_ids?.length) {
    return rt.pic_ids.slice(0, 3).map(id => `https://wx4.sinaimg.cn/orj360/${id}.jpg`).join(" | ");
  }
  return "";
}

async function scrapeAccount(cat, name, uid, startTs, endTs, cookie) {
  process.stdout.write(`  ${name} ... `);
  const posts = [];
  let page = 1;

  while (page <= 5) {
    try {
      const url = `/ajax/statuses/mymblog?uid=${uid}&page=${page}&feature=0`;
      const data = await httpGet("weibo.com", url, cookie);

      if (!data.ok || !data.data?.list?.length) break;

      const list = data.data.list;
      let hasOld = false;

      for (const p of list) {
        const ts = Math.floor(new Date(p.created_at).getTime() / 1000);
        if (ts < startTs) { hasOld = true; break; }
        if (ts > endTs) continue;

        const text = cleanText(p.text);
        const postUrl = `https://weibo.com/${p.idstr}`;
        const videoUrl = extractVideoUrl(p.page_info);
        const picUrls = extractPicUrls(p);

        posts.push({
          "账号分类": cat,
          "账号名称": name,
          "UID": uid,
          "发布时间": new Date(ts * 1000).toISOString().slice(0, 16).replace("T", " "),
          "微博正文": text.slice(0, 500) || "(无文字内容)",
          "视频链接": videoUrl,
          "图片链接": picUrls,
          "原始链接": postUrl,
          "点赞数": p.attitudes_count || 0,
          "评论数": p.comments_count || 0,
          "转发数": p.reposts_count || 0,
        });
      }

      if (hasOld) break;
      if (list.length < 20) break;
      page++;
      await new Promise(r => setTimeout(r, 600 + Math.random() * 800));
    } catch (e) {
      console.error(`\n  ⚠ ${name}: ${e.message}`);
      break;
    }
  }

  console.log(`→ ${posts.length}条`);
  return posts;
}

function demoData(cat, name, uid, startTs, endTs) {
  const ts = startTs + Math.floor(Math.random() * (endTs - startTs));
  return [{
    "账号分类": cat, "账号名称": name, "UID": uid,
    "发布时间": new Date(ts * 1000).toISOString().slice(0, 16).replace("T", " "),
    "微博正文": `[演示数据] ${name} 当前时段无抓取记录。配置真实Cookies后显示实际微博内容。`,
    "视频链接": "", "图片链接": "",
    "原始链接": `https://weibo.com/u/${uid}`,
    "点赞数": 0, "评论数": 0, "转发数": 0,
  }];
}

async function main() {
  const { startTs, endTs, dateStr } = getTimeWindow();
  const today = new Date().toISOString().slice(0, 10);

  // 确保输出目录存在
  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const logFile = path.join(OUTPUT_DIR, "weibo_scrape.log");

  function log(msg) {
    const ts = new Date().toISOString().slice(0, 19).replace("T", " ");
    console.log(`${ts} [INFO] ${msg}`);
    fs.appendFileSync(logFile, `${ts} [INFO] ${msg}\n`, "utf8");
  }

  log(`[${today}] 微博每日抓取开始`);

  let cookie = "";
  if (fs.existsSync(COOKIE_FILE)) {
    try {
      const cfg = JSON.parse(fs.readFileSync(COOKIE_FILE, "utf8"));
      if (cfg.enabled && cfg.cookie) cookie = cfg.cookie;
    } catch(e) {}
  }
  log(`模式：${cookie ? "真实抓取" : "演示模式"}，窗口：${dateStr} 08:40 → ${today} 08:40`);

  const allPosts = [];
  for (const [cat, name, uid] of ACCOUNTS) {
    await new Promise(r => setTimeout(r, 300));
    try {
      const posts = cookie
        ? await scrapeAccount(cat, name, uid, startTs, endTs, cookie)
        : demoData(cat, name, uid, startTs, endTs);
      allPosts.push(...posts);
    } catch (e) {
      log(`⚠ 抓取失败 [${name}]: ${e.message}，使用演示数据`);
      allPosts.push(...demoData(cat, name, uid, startTs, endTs));
    }
  }

  fs.writeFileSync(path.join(OUTPUT_DIR, `${dateStr}.json`), JSON.stringify(allPosts, null, 2), "utf8");
  log(`JSON备份：${dateStr}.json（${allPosts.length}条）`);

  if (fs.existsSync(EXCEL_GENERATOR)) {
    try {
      const out = execSync(`node ${EXCEL_GENERATOR} "${dateStr}"`, { cwd: path.join(SKILL_DIR, "scripts"), encoding: "utf8" });
      console.log(out.trim());
    } catch (e) {
      log(`Excel生成失败：${e.message}`);
    }
  }

  log(`抓取完成 ✅ 共 ${allPosts.length} 条`);
  console.log(`\n✅ 完成，共 ${allPosts.length} 条记录\n`);

  // 输出Excel路径供调用方读取
  const xlsxFile = path.join(OUTPUT_DIR, `${dateStr}.xlsx`);
  if (fs.existsSync(xlsxFile)) {
    console.log(`EXCEL_PATH:${xlsxFile}`);
  }
}

main().catch(e => { console.error("Fatal:", e); process.exit(1); });
