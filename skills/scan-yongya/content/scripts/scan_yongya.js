const puppeteer = require("puppeteer-core");

const URL =
  "https://www.jiaoyimao.com/lingxi/g1009207-3/?priceCondition=%7B%22price%22%3A%7B%22conditionList%22%3A%5B%2240000%22%5D%2C%22groupName%22%3A%22%E4%BB%B7%E6%A0%BC%E8%8C%83%E5%9B%B4%22%2C%22statConditionList%22%3A%5B%2240000%22%5D%7D%7D&searchCondition=%7B%22s3_equip_skill%22%3A%7B%22selectType%22%3A1%2C%22conditionList%22%3A%5B%227018093469081410054%40%E9%9B%8D%E9%9B%85%22%5D%2C%22conditionId%22%3A%227018093469081410054%22%2C%22statConditionList%22%3A%5B%22%E9%9B%8D%E9%9B%85%22%5D%2C%22conditionType%22%3A103%7D%7D&enforcePlat=3&newPage=true";

const BROWSER_PATHS = [
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
];

function findBrowserPath() {
  for (const p of BROWSER_PATHS) {
    try {
      require("fs").accessSync(p);
      return p;
    } catch {}
  }
  throw new Error("No supported browser executable found.");
}

async function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: findBrowserPath(),
    defaultViewport: { width: 1800, height: 1000, deviceScaleFactor: 1 },
    args: ["--disable-blink-features=AutomationControlled"],
  });

  try {
    const page = await browser.newPage();
    await page.setUserAgent(
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    );
    await page.goto(URL, { waitUntil: "networkidle2", timeout: 120000 });

    let stableRounds = 0;
    let lastCount = 0;
    for (let i = 0; i < 60; i += 1) {
      const count = await page.evaluate(() => {
        return document.querySelectorAll(".goods-item-role, .goods-item-for-big-img, .goodsList-item-v2, .goodsList-item")
          .length;
      });
      if (count > lastCount) {
        stableRounds = 0;
        lastCount = count;
      } else {
        stableRounds += 1;
      }
      await page.evaluate(() => {
        const candidates = [
          document.querySelector(".list-container"),
          document.querySelector(".goods-list-dom")?.parentElement,
          document.scrollingElement,
          document.documentElement,
          document.body,
        ].filter(Boolean);
        for (const el of candidates) {
          el.scrollTop = el.scrollHeight;
        }
        window.scrollTo(0, document.body.scrollHeight);
      });
      await delay(1800);
      if (stableRounds >= 4) {
        break;
      }
    }

    const debug = await page.evaluate(() => {
      const classCounts = {};
      for (const el of Array.from(document.querySelectorAll("[class]")).slice(0, 5000)) {
        for (const cls of Array.from(el.classList)) {
          classCounts[cls] = (classCounts[cls] || 0) + 1;
        }
      }
      return {
        title: document.title,
        bodyText: (document.body.innerText || "").slice(0, 4000),
        linkCount: document.querySelectorAll("a").length,
        cardCount: document.querySelectorAll(".goods-item-role, .goods-item-for-big-img, .goodsList-item-v2, .goodsList-item").length,
        scrollInfo: [
          document.querySelector(".list-container"),
          document.querySelector(".goods-list-dom")?.parentElement,
          document.scrollingElement,
          document.documentElement,
          document.body,
        ]
          .filter(Boolean)
          .map((el) => ({
            tag: el.tagName,
            className: el.className || "",
            scrollTop: el.scrollTop,
            scrollHeight: el.scrollHeight,
            clientHeight: el.clientHeight,
          })),
        classCounts: Object.entries(classCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 80),
        hrefSamples: Array.from(document.querySelectorAll("a"))
          .map((a) => a.href || "")
          .filter(Boolean)
          .slice(0, 50),
      };
    });
    console.log(`DEBUG_TITLE\t${debug.title}`);
    console.log(`DEBUG_LINKS\t${debug.linkCount}`);
    console.log(`DEBUG_CARDS\t${debug.cardCount}`);
    console.log(`DEBUG_TEXT\t${debug.bodyText}`);
    for (const item of debug.scrollInfo) {
      console.log(
        `DEBUG_SCROLL\t${item.tag}\t${item.className}\t${item.scrollTop}\t${item.clientHeight}\t${item.scrollHeight}`
      );
    }
    for (const [cls, count] of debug.classCounts) {
      console.log(`DEBUG_CLASS\t${cls}\t${count}`);
    }
    for (const href of debug.hrefSamples) {
      console.log(`DEBUG_HREF\t${href}`);
    }

    const cards = await page.evaluate(() => {
      const unique = new Map();
      const yongyaRe = /雍雅\*(\d+)/;
      const selectors = [
        ".goods-item-role",
        ".goods-item-for-big-img",
        ".goodsList-item-v2",
        ".goodsList-item",
      ];
      for (const selector of selectors) {
        for (const el of Array.from(document.querySelectorAll(selector))) {
          const text = (el.innerText || "").replace(/\s+/g, " ").trim();
          if (!text.includes("雍雅*")) continue;
          const href =
            el.querySelector("a[href*='/jg1009207/']")?.href ||
            "";
          const idMatch = href.match(/\/(\d+)\.html/);
          const yongyaMatch = text.match(yongyaRe);
          unique.set(href || text, {
            goodsId: idMatch ? idMatch[1] : "",
            href,
            text,
            yongya: yongyaMatch ? Number(yongyaMatch[1]) : null,
          });
        }
      }
      return Array.from(unique.values());
    });

    cards.sort((a, b) => {
      const ay = a.yongya ?? -1;
      const by = b.yongya ?? -1;
      return by - ay || a.goodsId.localeCompare(b.goodsId);
    });

    console.log(`TOTAL\t${cards.length}`);
    for (const item of cards) {
      console.log(
        `CARD\t${item.yongya ?? ""}\t${item.goodsId}\t${item.href}\t${item.text}`
      );
    }
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
