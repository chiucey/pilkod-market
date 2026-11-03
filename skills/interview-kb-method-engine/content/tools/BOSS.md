# Boss直聘岗位抓取（skill 内置能力）

## 命令

三个文件，职责清晰：

| 文件 | 职责 |
|---|---|
| `boss.mjs` | **抓岗位列表**（Node + CDP，零配置） |
| `boss_jd.mjs` | **抓 JD 正文**（Node + CDP） |
| `boss.py` | **解码 / 筛选 / 合并 / 备战 / 自检**（Python，纯本地） |

```bash
cd <包根目录>/tools     # 命令都在 tools/ 下跑；脚本不依赖目录名

# 0) 自检（改过代码或换机器后先跑）
python main.py boss selftest      # 或简写 python main.py selftest

# 1) 抓岗位（零配置：自动探测浏览器、自动处理扫码登录）
node boss.mjs harvest --query 内容运营 --city 北京
node boss.mjs harvest --queries 内容生态,创作者运营,社区运营 --city 北京
node boss.mjs help

# 2) 筛选分级（纯本地）
python main.py boss filter --file <boss_jobs.json> --out <筛选.md>

# 3) 抓 JD 正文（可选，强烈建议——匹配分析会准得多）
node boss_jd.mjs --file <boss_jobs.json> --limit 25

# 4) 逐条备战分析
python main.py bosstojob --jd <boss_jd.json> --top 8

# 5) 突破单次上限：换关键词多抓几轮后合并
python main.py bossmerge --files "<数据目录>/boss_*.json" --out "<数据目录>/boss_all.json"

# 辅助
python main.py boss decode --text "<含PUA字符的薪资>"
python main.py boss keywords
```

### 数据落在哪（重要）

代码在 skill 的 `tools/` 下（可分发），**数据一律写到 skill 之外**，
由 `boss.mjs` 的 `dataDir()` 按以下顺序选第一个可写的：

1. `--data-dir <目录>`（显式指定）
2. 环境变量 `BOSS_DATA_DIR`
3. 当前工作目录下的 `.boss/`
4. skill 同级目录的 `boss_data/`
5. 系统临时目录

**为什么必须分开**：skill 要分发给别人，里面混入抓取结果（含真实求职数据）
和浏览器登录态是不可接受的。

### 自检命令（重要）

```bash
python main.py boss selftest    # 退出码非 0 表示有回归
```

它用**内置真值**验证三件事，换任何机器都能离线跑：

| 检查项 | 用例数 | 说明 |
|---|---|---|
| PUA 薪资解码 | 13 | 每条对应一个真实抓到的 DOM 值，真值来自页面明文接口 |
| 薪资解析 | 4 | `salary_mid` / `months_bonus` 的月薪中值与年包倍数 |
| 筛选分级 | 4 | 合成样本验证 A/C 分级与排除词（外包、兼职实习） |

**为什么必须有它**：PUA 映射曾被写错成 `\uE030`+n = n（差一位），
导致所有薪资整体偏高约一倍（`12-20K` 解成 `23-31K`），
而错误结果**看起来依然合理**，常识判断无法发现——只能靠回归测试兜住。
实测：把错误映射注入回去，自检立刻报 13 项失败并以退出码 1 结束。

`python main.py validate`（校验卡片）也会顺带跑这个自检。

## 三、JD 正文抓取（`boss_jd.mjs`）

列表页只给职位名/薪资/公司/标签，**没有 JD 正文**。但每条岗位都带
`href`（`/job_detail/xxx.html`），顺着它抓详情页即可补齐。

```bash
node boss_jd.mjs --file ../boss_jobs.json --out ../boss_jd.json --limit 25
python main.py bosstojob --jd ../boss_jd.json --out ../boss_JD分析.md --top 8
```

### 为什么读 DOM 而不是调接口

详情接口 `/wapi/zpgeek/job/detail.json?securityId=...` 会返回
`{"code":17,"message":"缺少必要参数"}` —— 它还需要前端计算的额外参数。
所以直接读**渲染后的 DOM**：

| 选择器 | 内容 |
|---|---|
| `.job-sec-text` 第 0 个 | **JD 正文**（岗位职责/任职要求） |
| `.job-sec-text` 第 1 个 | 公司介绍 |
| `.job-detail-section` | 各分块（含竞争力分析、BOSS 安全提示等噪声） |

脚本用文本特征把公司介绍从 JD 里剔除（开头是"我们/公司/成立于/愿景"或含
"有限公司/成立于20xx"的判为公司介绍）。

实测：**24/25 成功**（96%）。失败的那条是"线上兼职"类岗位，详情页结构不同。

### 与 skill 打通

`python main.py bosstojob` 会把每条 JD 写成临时文件喂给 `job` 命令，
产出「岗位职责画像 / 简历匹配度 / 最匹配面经 / 预判问题」四段分析。

实测某岗位匹配度 89%，并给出简历缺口（如"创作者"经历需补齐）。

## 一、PUA 薪资解码（硬知识，务必保留）

Boss 用自定义字体 **`kanzhun-mix`** 把薪资里的**数字**替换成 Unicode 私用区(PUA)字符。

**映射不是码位偏移**，实测表如下（这是踩过坑的地方）：

```
\uE031 → 0    \uE032 → 1    \uE033 → 2    \uE034 → 3    \uE035 → 4
\uE036 → 5    \uE037 → 6    \uE038 → 7    \uE039 → 8    \uE03A → 9
```

> ⚠️ **曾经误以为映射是 `\uE030`+n = n**，即 `\uE030→0, \uE031→1, ...`。
> 这个错误让**所有薪资整体偏高一位**，例如真实 `12-20K` 被解成 `23-31K`。
> 它很隐蔽：偏差结果仍然"看起来合理"，常识判断无法发现。

### 如何得到真值（可复现的验证方法）

页面自身的接口返回**明文**薪资，是最好的真值来源：

```js
// 在页面上下文里调用（同源、自动带 Cookie）
fetch('/wapi/zpgeek/search/joblist.json?scene=1&query=内容运营&city=101010100&page=1&pageSize=30',
      { credentials: 'include' })
// => zpData.jobList[].salaryDesc  是明文，如 "12-20K"、"11-22K·16薪"
```

把它与 DOM 卡片的**原始 PUA 码位**按岗位名对齐，即可逐条验证映射。
当前实测结果：**13/13 完全吻合** —— 这 13 条真值已内置进 `boss.py` 的
`SELFTEST_CASES`，随时可用 `python main.py boss selftest` 复现。

独立佐证：把每个 PUA 码位和每个数字（0-9）都用薪资节点同款字体渲染成位图，
按裁剪后的形状做逐像素比对，即可反推出映射。实测每个码位的最佳匹配
margin 全部 > 0.29（次优差距明显），且字形宽高比也吻合
（`E032` 宽高比 0.381 = 数字 "1" 的窄字形）。

### 常见的两个坑

1. **`textContent` / `innerText` 返回的都是 PUA 字符**，浏览器不会替你还原。
2. **任何"清理私用区"的正则都会把薪资数字一起删掉**，例如
   `replace(/[\uE000-\uF8FF]/g, '')` 会让薪资变成 `-K`。

正确做法：按上表把 `\uE031..\uE03A` 映射成 `'0'..'9'`
（见 `boss.py::decode_pua`，以及 `boss.mjs` 里注入页面的同款 `decode`）。

## 二、翻页：**不要点按钮，走页面接口**

这一节是被推翻重写过的，记录了真实的排查过程。

### 曾经的做法（❌ 不可靠，已废弃）

点 `a.more-job-btn`（文案「查看更多信息」）。它**有时能用**（"内容运营"曾靠它抓到 150 条），
但换个关键词就只出 15 条，产出差 10 倍。深挖后发现根因：

| 做法 | 实测结果 |
|---|---|
| `window.scrollTo` / 滚 `ul.rec-job-list` | ❌ 无效：`scrollHeight === clientHeight`，它根本不是滚动容器 |
| `b.scrollIntoView()` + `b.click()` | ❌ 按钮 `rect.top ≈ 1408`（视口外），点击落在空白处 |
| CDP 真实鼠标点击（`Input.dispatchMouseEvent`） | ❌ 同样失败，因为按钮仍在视口外 |
| `window.scrollBy(0, top-400)` 想滚过去 | ❌ **完全无效**：`top` 从 1408 → 1405，滚不动 |

结论：Boss 这版布局里 window 不可滚，按钮始终在视口外，**程序化点击不可靠**。

### 现在做法（✅ 稳定）

直接调**页面自身的搜索接口**（同源 + `credentials:'include'` 自动带 Cookie）：

```js
fetch('/wapi/zpgeek/search/joblist.json?scene=1&query=内容运营&city=101010100&page=1&pageSize=30',
      { credentials: 'include' })
// => zpData.jobList[]，其中 salaryDesc 是**明文**，连 PUA 解码都不需要
```

实测：page 1-5 每页 30 条全部成功 → **151 条**。稳定可复现。

### 单次上限 150 不是配置，是风控

服务端返回 `totalCount: 300`，但：

```
page 1-5 : code 0, 每页 30 条, hasMore: true, total: 300
page 6   : {"code":37,"message":"您的环境存在异常."}
```

即使每页间隔 3.5 秒、被拦后退避 30 秒重试同一页，**第 6 页依然被拒**。
所以单次查询实际上限 = 5 页 × 30 = **150 条**。

**想要更多岗位，正确做法是换关键词多抓几轮再合并**（风控按"单次查询"计）：

```bash
python main.py bossmerge --files "boss_*.json" --out boss_all.json
```

### 抓取速度与两个可调参数

实测一次「内容运营」抓满 150 条约 **12 秒**（优化前 19 秒）。

提速的关键是**两处都不再"白等"**：

| 参数 | 默认 | 说明 |
|---|---|---|
| `--page-gap <ms>` | `1200` | 每页间隔。实测正常页响应极快（接口瞬时返回）。调大可降低被风控概率 |
| `--fetch-timeout <ms>` | `4000` | 页面内单次请求超时 |

**为什么必须有 `--fetch-timeout`**：被风控时 Boss 会让请求挂住不返回。
不设页面内超时的话，外层 CDP 要等满 20 秒才超时，**每页白等 22 秒
（20s 超时 + 2.2s 间隔），而且拿不到任何数据**。
加上页面内 `AbortController`（4 秒）后，失败立刻返回。

**失败即停**：一旦某页返回非 0，说明已触发风控，后面几页同样会挂 ——
继续请求只是浪费时间，脚本会立即停止翻页并给出提示。

> 想更保守（降低被风控概率）：`--page-gap 3000 --fetch-timeout 6000`。
> 想更快（前几页本来就快）：`--page-gap 800`。

### 可用的选择器（读首屏 DOM 时用）

```
卡片:   li.job-card-box
列表:   ul.rec-job-list          （注意：不是滚动容器）
容器:   .job-list-container
薪资:   .job-salary
公司:   .boss-name / .company-name / .brand-name
地点:   .company-location / .job-area
标签:   .tag-list li / .job-labels span
详情:   a[href*="/job_detail/"]  ← 抓 JD 正文靠它
翻页按钮: a.more-job-btn          （「查看更多信息」——已不用，见上）
```

## 三、抓取前提（环境相关，非 skill 逻辑）

1. **浏览器能起来 + profile 目录可写**。受限环境下会报
   `Lock file can not be created! Error code: 5` 并立即退出。
2. **必须先登录**。未登录访问搜索/推荐页会跳 `https://www.zhipin.com/web/user/`，
   卡片数恒为 0。
3. **profile 不能被其他浏览器实例占用**，否则 rod/调试端口拿不到
   （`Failed to get the debug url`）。跑之前关掉同 profile 的浏览器，
   并清理 `SingletonLock` / `SingletonSocket` / `SingletonCookie` / `DevToolsActivePort`
   （`boss.mjs` 已自动清理）。

登录态持久化在 profile 目录里，**扫码一次即可长期复用**。

## 四、MCP 线路（不推荐，仅说明）

上游另有一个 Go 写的 MCP 版本（`namejiahui/mcp-boss-zp`），提供
`get_current_jobs` 取**当前屏**岗位（约 15 条，不含翻页）。

**但本包不附带它的安装说明、也不推荐走这条路**，原因：

| 对比 | 该 MCP | 本包内置 `boss.mjs` |
|---|---|---|
| 获取量 | 15 条（只读当前屏） | **约 150 条**（走接口翻页） |
| 前置条件 | 需自行编译（本机无 Go、上游无 Release） | 只需 Node + 浏览器 |
| 维护状态 | 上游 0.3.0 无发布渠道 | 随本包一起演进 |

简言之：**用 `boss.mjs` 即可**。`mcp-boss-zp` 那条路对本包用户没有增量价值，
且它的登录判定还存在一个方向写反的 bug（见 `boss.mjs` 内的注释）。

## 五、筛选分级逻辑

### 用工性质单独分类（外包 / 兼职 / 实习 / 正编）

这三类是**不同性质**，不能混成一个"排除项"：

| 性质 | 含义 | 默认处理 |
|---|---|---|
| **正编** | 与企业直接签劳动合同 | 不惩罚 |
| **外包** | 正式雇佣，但合同签第三方劳务公司（影响履历归属/晋升/转正） | **降权 −1.0，不排除** |
| **兼职** | 非全日制/按次结算，无正式劳动关系 | 默认归 C |
| **实习** | 面向在校生，通常为转正前置 | 默认归 C |

判定在 `classify_nature()`，**只看岗位名 + 公司名，不看 tags**。
踩过的坑：`线上` 这个弱词会命中正常 tag（如"线上运营"），把正编岗误判成兼职。

优先级：**实习 > 兼职 > 外包 > 正编** —— 一个"外包公司的实习岗"应判为实习，
因为对应聘者的实际要求是学生身份。

薪资形态作为兜底信号：`元/天` → 实习，`元/时` → 兼职。

### 三个词表

- `CORE_KEYWORDS`：命中加分（内容生态/内容运营/社区运营/创作者运营/垂类/用户增长…）
- `EXCLUDE_PATTERNS`：命中扣分并直接归 C（销售/纯工程/直播带货/客服）
- `NATURE_PATTERNS` + `NATURE_PENALTY`：用工性质（见上表）

分级：`A`(≥3.5 且无排除) / `B`(≥2) / `C`(有排除、性质默认排除、或低分)。
薪资也参与打分（≥30K +1.5，≥25K +1，<18K −1）。

### 用法

```bash
# 默认：正编参与评级，外包降权，兼职/实习归 C
python main.py boss filter --file boss_jobs.json

# 只看某性质（此时该类不再被降权，会正常分 A/B/C）
python main.py boss filter --file boss_jobs.json --nature 外包
python main.py boss filter --file boss_jobs.json --nature 实习

# 让外包不因降权掉级
python main.py boss filter --file boss_jobs.json --keep 外包
```

输出会先打印**性质分布**（如 `正编=140 实习=20 兼职=4 外包=1`），
markdown 报告里有独立的「性质」列。

**词表要按你自己的简历改** —— 直接编辑 `boss.py` 顶部的几个字典。

## 六、已知局限

- **JD 正文要靠 `boss_jd.mjs` 单独抓**：列表接口只给职位名/薪资/公司/标签，
  但每条都带 `href`，顺着抓详情页即可（实测 96% 成功）。
- **搜索池质量取决于关键词**。用单一"内容运营"搜出的大量小公司岗，
  不如用"社区运营""创作者运营""内容生态"等**贴近你简历强项**的词。
- **外包判定依赖岗位名**。有些外包岗不写"外包"，而是靠公司名（如"XX信息技术"
  这类劳务公司）才能识别，纯关键词会有漏网。要更准需维护一份外包公司名单。
- 抓取频率别太猛：短时间高频翻页对账号有风控风险，建议手动触发、单次抓完即停。
