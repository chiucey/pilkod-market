# 朗读系统

模板的朗读引擎支持两条音源，自动降级。**默认走第一条**：

| 音源 | 何时用 | 优点 | 代价 |
|---|---|---|---|
| **离线 mp3**（`AUDIO_MANIFEST`） | **默认**；要固定音色、可离线、变速不糊 | 音质与音色稳定，任何机器一致 | 要先生成音频，页面上多出 `assets/audio/` |
| **浏览器语音合成**（`speechSynthesis`） | 有「不下载外部文件」这类约束，或只求能听 | 零成本、零依赖 | 音色取决于系统；没有中文音色就哑；变速会变调 |

两者都不可用时，朗读入口整体隐藏，不留一个点了没反应的按钮。

默认音色固定为**「电台男主播」**（`voice_id: Chinese (Mandarin)_Radio_Host`）。

## 一、段落与音频怎么对齐

靠两个属性，不靠 DOM 顺序：

- `data-tts-c`：章节 id（与 `section.chapter` 的 id 一致）
- `data-tts-i`：章内序号，从 0 连续

```html
<h3 class="h h--3" data-tts-c="ch1" data-tts-i="0">小标题</h3>
<p class="prose" data-tts-c="ch1" data-tts-i="1">正文段落。</p>
```

引擎在运行时按这两个属性建「章 → 段落队列」，再按 `[chapter, index]` 去
清单里找音频文件。靠 `querySelectorAll` 猜顺序是这类实现最常见的 bug：
章节重排之后就会「念 A 段高亮 B 段」，而且不报错。

## 二、清单结构

`AUDIO_MANIFEST` 写在页面 `<script>` 里，紧跟模板的引擎之前：

```js
var AUDIO_MANIFEST = {
  generatedFrom: "make-audio.mjs",
  speed: 0.95,
  emotion: "neutral",
  voices: [{ id: "Chinese (Mandarin)_Radio_Host", name: "电台男主播" }],
  blocks: [
    { i: 0, n: 0, chapter: "ch1", kind: "h3",
      text: "小标题",
      audio: { "Chinese (Mandarin)_Radio_Host": "assets/audio/Chinese_Mandarin__Radio_Host/ch1_000.mp3" } },
    …
  ]
};
```

- `blocks[].i` = 章内序号（对应 `data-tts-i`）
- `blocks[].chapter` = 章 id（对应 `data-tts-c`）
- `blocks[].n` = 全局序号，仅用于生成顺序，运行时不用
- `blocks[].audio` = 音色 id → 相对路径。**相对路径以 index.html 为基准**
- `blocks[].text` = 这一段念的内容，**重跑脚本时靠它比对、判断能否复用旧音频**
- `voices[]` = 可切换的音色列表；一个音色也可以
- **默认音色** = 清单里 `name` 为「电台男主播」的那一个；没有这一项时取第一个

音频文件名用 `<章id>_<章内序号>.mp3`（如 `ch1_000.mp3`），
不用全局流水号——流水号会让「插一段」导致后面所有音频集体错位。

没有 mp3 时，把 `AUDIO_MANIFEST` 写成 `null`：

```js
var AUDIO_MANIFEST = null;
```

## 三、生成 mp3（固定音色的标准做法）

**默认音色固定为「电台男主播」**（`voice_id: Chinese (Mandarin)_Radio_Host`）。
它是叙事向音色，念整本书最稳；系统彩蛋音（Eddy / Flo / Grandma 之类）念长文非常难听。

### 一条命令搞定

```bash
node scripts/make-audio.mjs <交付目录>/index.html
```

脚本做完全部工作：抽段落 → 按 (章, 序号) 排序 → 切块 → 调 matrix TTS 合成 →
下载 mp3 → 把 `AUDIO_MANIFEST` 写回 HTML。

常用选项：

| 选项 | 作用 |
|---|---|
| `--dry-run` | 只打印每段要念的文本，不合成、不改文件（先看一遍再花钱） |
| `--voice-id "<id>"` | 换音色，默认 `Chinese (Mandarin)_Radio_Host` |
| `--voice-name "<名>"` | 音色显示名，写进清单的 `voices[].name`，默认「电台男主播」 |
| `--speed <0.5–2>` | 语速，默认 0.95 |
| `--emotion <名字>` | 情感，默认 `neutral` |
| `--out <目录>` | mp3 输出目录，默认 `<html 所在目录>/assets/audio` |
| `--force` | 已存在的 mp3 也重新生成 |

产出：

```
assets/audio/Chinese_Mandarin__Radio_Host/000.mp3
assets/audio/Chinese_Mandarin__Radio_Host/001.mp3
…
```

目录名规则：音色 id 里**连续的**非字母数字折叠成一个下划线。
`Chinese (Mandarin)_Radio_Host` → `Chinese_Mandarin__Radio_Host`。
清单里的路径必须跟磁盘上完全一致，`check-page.mjs` 会逐个核对。

### 上游会限流，脚本自己扛

matrix TTS 有速率限制，超了会返回 `err_code: 429`，
提示语是「retry the SAME request after a brief delay」。
脚本对此的策略：

1. 按 429 退避重试（3s → 6s → 12s → 24s → 45s 封顶）
2. 每轮把批次缩小（10 → 3 → 1），别再一股脑打过去
3. 最多 8 轮；实在不成就把该段排除出清单，引擎自动退回浏览器合成
4. **已下载的文件不会重做**——重跑脚本只补没成功的那几段

所以断了网、或中途失败，直接重跑同一条命令即可，不要从头删文件重来。

### 手动做法（脚本不可用时）

```bash
# 1. 看参数
mcode-tools connector tools --keyword tts
mcode-tools connector tool connector__matrix__batch_text_to_audio

# 2. 合成（一次最多 10 段），output_file 是下载后的文件名
mcode-tools connector call connector__matrix__batch_text_to_audio \
  --args '{"requests":[{"text":"小标题","voice_id":"Chinese (Mandarin)_Radio_Host","speed":0.95,"emotion":"neutral","output_file":"000.mp3"}]}'
# 返回 success_items[].node_id 与 file_name

# 3. 下载（短时效地址，不要自己拼 URL）
mcode-tools get-asset-url <node_id>
curl -L -o assets/audio/Chinese_Mandarin__Radio_Host/000.mp3 "<下载地址>"

# 4. 把结果按下面的结构写进 AUDIO_MANIFEST
# 5. 核对：node scripts/check-page.mjs index.html
```

清单结构：

```js
var AUDIO_MANIFEST = {
  generatedFrom: 'make-audio.mjs',
  speed: 0.95,
  emotion: 'neutral',
  voices: [{ id: 'Chinese (Mandarin)_Radio_Host', name: '电台男主播' }],
  blocks: [
    { i: 0, n: 0, chapter: 'ch1', kind: 'h3', text: '小标题',
      audio: { 'Chinese (Mandarin)_Radio_Host': 'assets/audio/Chinese_Mandarin__Radio_Host/000.mp3' } }
  ]
};
```

`i` 是章内序号、`n` 是全局序号、`chapter` 是章 id、`kind` 是元素类型、
`text` 是这一段念的内容。引擎按 `chapter + '#' + i` 把音频和段落对上。

**换音色**：调 `connector__matrix__get_voice_list` 看全部音色（当前 327 个），
选一个新的 `voice_id`，用 `--voice-id` 传进去，并把 `--voice-name` 改成对应的
显示名。引擎在清单里**按名字**找「电台男主播」，改名后默认音色也跟着变。

### 什么情况下不要走 mp3 这一路

mp3 流程的**最后一步必须把音频文件下载到本地**（上面第 4 步的 `curl`，
或任何等价的下载动作）。所以：

- 用户或任务里带了「**不引外部资源 / 不下载外部文件 / 离线自包含**」这类约束时，
  mp3 流程整条作废——不是「尽量少用」，是用不了。
- 这种情况下走浏览器语音合成（`AUDIO_MANIFEST` 留 `null`），并在交付说明里写明
  「朗读依赖读者系统的中文音色；系统没装中文语音的机器上这一页会发不出声」。
- 别把 `AUDIO_MANIFEST` 填成一个指向远程 URL 的清单来绕开下载：
  模板要求单文件离线可用，外链音频会在离线时整段静默失败，
  而且校验脚本查的是**本地文件是否存在**，远程 URL 会被判成「文件不存在」。

判断标准很简单：**这份音频要不要随交付物一起给读者？** 要，就得落盘；
不要，且约束不许落盘，就用合成。

### 段落增删之后

`make-audio.mjs` 自己处理这件事，不用手工改名：

- 音频文件名是 `<章id>_<章内序号>.mp3`（如 `ch1_000.mp3`），**不是全局流水号**——
  流水号会让「插一段」导致后面所有音频集体错位
- 重跑时按 **（章, 序号）** 找回旧清单里的对应项，比对**文本**：
  文字没变就复用旧音频（顺手把文件名规范成当前命名），文字变了才重新合成

所以插一段、删一段、改一段文字之后，直接重跑脚本即可——
只有真正变了的那几段会重新合成，其余照旧复用。

老项目里用全局流水号命名的音频，第一次跑新脚本时会被改名归位，不会错配。

### 合成失败或音频缺失

引擎遇到缺音频的段落会跳过并在面板提示，不会卡死。交付说明里要写清
哪几段没有声音——读者以为能听却听不到，比一开始就说清楚更糟。

## 四、合成音源不可用时的行为

浏览器内置合成不是处处可用：无语音包的系统、精简容器、某些 Electron 运行时里，
`speechSynthesis` 对象存在、也列得出音色，但 `speak()` 根本不念。

引擎对此有三道防线，**目的只有一个：让读者看到明确原因，而不是被假装在朗读**：

1. **开始前**：没有中文音色就直接拒绝并说明「这台设备没有可用的中文语音」。
   只取中文音色——系统自带的英文音色念中文非常难听。
2. **秒结束**：一段话在 150ms 内就「念完」而文本超过 8 个字，说明一个字都没念。
   连续两段如此即判定不可用。
   这一条最关键：**失败时绝不能一段段跳过**——那会瞬间跑完整章，
   读者只看到「已读完」，完全不知道出了什么事。
3. **卡住**：开始念之后超过「文本量 × 0.3 秒 + 6 秒」还没结束，判为卡死并停止。

停止时会给出可执行的建议（改用离线 mp3 音频），而不是一个没有出处的静默失败。
如果目标机器必须稳定朗读，就配 mp3 清单——那是唯一不依赖设备环境的路径。

## 五、跟随滚动的行为

朗读时当前段落滚到视口垂直中间，段落比视口高时改为贴近上方。
几个必须保留的行为：

- **读者自己翻页时暂停跟随 6 秒**，然后自动恢复。
  永久停掉是最伤的 bug：一次误触滚轮就让朗读失去跟随。
- **区分「程序滚动」和「读者滚动」**：程序滚动会登记目标位置，
  滚动事件里靠「离目标的距离在变小」判断是不是自己的动画。
  时间锁常常在动画还没走完时就失效，把自己的滚动误判成读者翻页。
- **跳转章首用瞬时定位，不用平滑滚动**。两个滚动动画会互相抢：
  在途的那个仍按自己的终点飞，最后把页面停在错误章节。
  瞬时定位一定落在章首，之后由跟随滚动接管后续位置。
- **跳转章首不用 `scrollIntoView`**：它虽然尊重 `scroll-margin-top`，
  但不会登记程序滚动目标，会被误判成读者翻页，接下来 6 秒不跟随。
- **起播必须在用户点击的同步调用栈里完成**。浏览器自动播放策略只认用户手势，
  `setTimeout` 之后再调 `audio.play()` 会被静默拦掉——页面显示「朗读中」
  却没有声音。
- **封面「开始阅读」要点章首而不是首段**：起播瞬间的跟随滚动会把首段居中，
  章标题直接被甩出视口，读者落在一个没有上下文的地方。引擎用一次性开关
  挡掉那一次跟随滚动，之后恢复正常。

## 六、朗读界面

- **右侧竖条**（桌面）/ **底部横条**（手机）：播放暂停、上一章、下一章、
  停止、音色、展开面板。不用展开就能控制。
- **面板**：状态、当前章名、当前段文字、按钮、语速、音色；可最小化（收成状态条，
  朗读照常继续）、可最大化（整页听读，当前段居中显示，琥珀底标出）。
- **面板里也放一份当前段文字**：听读时不用再抬头找正文。
- **Esc 逐层退出**：音色菜单 → 最小化 → 最大化 → 关闭。

### 播放键要跟着状态换图标（这条容易漏）

同一个键，停着显示**播放键 ▶**，念着显示**暂停键 ⏸**，暂停之后恢复播放键。
同时提示文字也要跟着走：停着是「播放 / 暂停」，念着是「暂停」。

引擎里就一行，在 `setState` 里：

```js
if (barToggle){
  barToggle.classList.toggle('is-on', playing);
  barToggle.setAttribute('data-tip', playing ? '暂停' : '播放 / 暂停');
  barToggle.setAttribute('aria-label', playing ? '暂停' : '播放 / 暂停');
}
```

配套的 CSS 模板里已经有了：

```css
.ttsbar__btn .ico-pause{ display:none; }
.ttsbar__btn.is-on .ico-play{ display:none; }
.ttsbar__btn.is-on .ico-pause{ display:block; }
```

**为什么不能省**：按钮上的图标是唯一的播放状态提示。少了这行，按钮永远长一个样，
播放中读者也看不出还能不能暂停，只能盲点——而且不报任何错，页面看着完全正常。
面板里的主按钮同理，文字要在「▶ 播放」和「⏸ 暂停」之间换。

`check-page.mjs` 会查这一项：脚本里没有 `barToggle` 的 `is-on` 切换就直接 FAIL。

## 七、音频体积

一段 30 字的 mp3 约 40–60KB。一份 13 章、168 段的书约 10MB。

- 只给要朗读的段落配音频，不需要朗读的段落不要生成
- 音频必须与页面一起部署：页面在 `index.html`，音频在 `assets/audio/`
- 部署后确认清单里每个路径都能 200 返回，缺一个就是那一段没声音
