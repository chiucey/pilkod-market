# 18 个 AI-GIS 智能问图平台实战踩坑(2026-08)

> **来源**:AI-GIS 智能问图平台 v0.1.0 → v0.4.0 四个月迭代实战沉淀
> **项目**:FastAPI + 原生 JS + Cesium + MCP (stdio) + 多 server 聚合
> **场景**:天地图 / GeoServer / SuperMap / GeoWay / ArcGIS / 本地 SHP / QGIS 7 种数据源

每个踩坑都附"症状 + 根因 + 解决 + 预防"四件套,可直接抄到自己的项目。

---

## 一、AI 智能问答相关(7 个)

### 1. F5 刷新后 AI 记忆清空

**症状**:用户发了一堆对话,按 F5 刷新浏览器,对话全没了。
**根因**:对话历史只在浏览器内存(`window.chatHistory`),无持久化。
**解决(用户接受现状)**:
- v0.4.0 行为:对话历史只在内存,F5 刷新清空
- 在 UI 明确提示"刷新会清空对话"
**预防(要做持久化)**:
- IndexedDB:`idb` 库 5 行代码搞定
- 后端 DB:对话长时保留,但敏感信息要加密
- 折中:对话只保留 24h,过期清理

### 2. LLM 工具调用解析漏字段

**症状**:LLM 返回的"工具调用 JSON",后端只解析了 `name` 和 `arguments`,`id` 字段丢了,下次工具结果回传时 LLM 不认。
**根因**:OpenAI Function Calling 标准字段是 `{id, type, function: {name, arguments}}`,有些 LLM(通义/文心)返回字段顺序/嵌套不同。
**解决**:
```python
def parse_tool_call(raw: dict) -> dict:
    """统一解析,容忍 4 种 LLM 返回格式"""
    # OpenAI 标准
    if "function" in raw:
        return {
            "id": raw.get("id", str(uuid.uuid4())),
            "name": raw["function"]["name"],
            "arguments": json.loads(raw["function"]["arguments"])
        }
    # 通义/文心: 字段平铺
    if "name" in raw and "arguments" in raw:
        return {
            "id": raw.get("id", str(uuid.uuid4())),
            "name": raw["name"],
            "arguments": json.loads(raw["arguments"]) if isinstance(raw["arguments"], str) else raw["arguments"]
        }
    # Claude: content[].type=="tool_use"
    if raw.get("type") == "tool_use":
        return {"id": raw["id"], "name": raw["name"], "arguments": raw["input"]}
    raise ValueError(f"无法解析工具调用: {raw}")
```

### 3. 流式输出 buffer 太大,内存爆

**症状**:LLM 一次返回 8k tokens,前端 5 秒内全部进 DOM,内存 500MB。
**根因**:EventSource 没有背压,后端一直推,前端不节流。
**解决**:
- **后端限速**:每 50ms flush 一次
```python
async def event_stream():
    buf = []
    last_flush = time.time()
    async for chunk in llm.stream(prompt):
        buf.append(chunk)
        if time.time() - last_flush > 0.05:
            yield f"data: {''.join(buf)}\n\n"
            buf = []
            await asyncio.sleep(0)  # 让出事件循环
    if buf: yield f"data: {''.join(buf)}\n\n"
```
- **前端节流**:requestAnimationFrame 合并
```js
let pending = '';
let scheduled = false;
es.onmessage = e => {
    pending += e.data;
    if (!scheduled) {
        scheduled = true;
        requestAnimationFrame(() => {
            appendToUI(pending);
            pending = '';
            scheduled = false;
        });
    }
};
```

### 4. WebSocket 重连风暴

**症状**:网络抖动,前端疯狂重连,5 秒内重试 100 次,后端连接数爆。
**根因**:没用退避策略。
**解决**:
```js
let retry = 0;
function connect() {
    const ws = new WebSocket(url);
    ws.onclose = () => {
        const delay = Math.min(30000, 1000 * Math.pow(2, retry++));
        setTimeout(connect, delay);
    };
    ws.onopen = () => { retry = 0; };  // 连上重置
}
```

### 5. LLM 返回的"工具调用参数"格式错

**症状**:LLM 说"查浙江省的 POI",返回 `{"province": "浙江"}`,但 GIS API 要 `{"region_code": "330000"}`。
**根因**:LLM 不知道 GIS 业务字段。
**解决 — Tool 描述里给清楚**:
```python
tools = [{
    "type": "function",
    "function": {
        "name": "search_poi",
        "description": "在指定行政区划内搜索 POI。行政区划用 6 位 adcode(国标代码),如浙江省=330000",
        "parameters": {
            "type": "object",
            "properties": {
                "region_code": {
                    "type": "string",
                    "description": "6 位国标 adcode,例:330000=浙江省,110000=北京市"
                },
                "keyword": {"type": "string"}
            },
            "required": ["region_code"]
        }
    }
}]
```

### 6. LLM 调用工具后没回传结果,死循环

**症状**:LLM 调了工具,后端执行完了,结果回传给 LLM,但 LLM 又调一次同样的工具,反复。
**根因**:工具结果没标 "role":"tool" + "tool_call_id" 匹配。
**解决**:
```python
# 错误的回传
messages.append({"role": "assistant", "content": "", "tool_calls": [tool_call]})
messages.append({"role": "user", "content": tool_result})  # ← role 错了
# 正确的回传
messages.append({"role": "tool", "tool_call_id": tool_call["id"], "content": tool_result})
```

### 7. SSE nginx 反代 buffer 卡死

**症状**:本地跑 SSE 正常,部署到 nginx 后第一次连接卡住,要等 60s 才出第一段数据。
**根因**:nginx 默认 `proxy_buffering on`,会把 SSE 攒到 buffer 满才推。
**解决**:
```nginx
location /api/stream {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_buffering off;           # ← 关键
    proxy_cache off;
    chunked_transfer_encoding off;
    proxy_set_header Connection '';
    add_header X-Accel-Buffering no;  # ← 后端响应头也加
}
```

---

## 二、地图 / Cesium 相关(5 个)

### 8. 天地图 POI 一直不显示

**症状**:调了天地图 API,返回 200 + 数据,但 Cesium 地图上没标记。
**根因**:`clearMap(null)` 传 null,Cesium 抛错被 catch 吞了,后续 add 全部失败。
**解决**:
```js
async function clearMap(map) {
    try {
        if (map && typeof map.clear === 'function') {
            map.clear();
        } else {
            console.warn('map 对象异常,跳过清空');
        }
    } catch (e) {
        console.warn('clearMap 容错:', e);
        // 继续执行,不让后续 add 失败
    }
}
```

### 9. Cesium Ion 默认 token 过期

**症状**:用 Cesium 默认 token,30 天后所有地球影像变白。
**根因**:Cesium Ion 试用 token 30 天过期。
**解决 — 国内项目用天地图 token 替代**:
```js
const viewer = new Cesium.Viewer('cesiumContainer', {
    imageryProvider: new Cesium.UrlTemplateImageryProvider({
        url: `https://t{s}.tianditu.gov.cn/img_w/wmts?service=wmts&request=GetTile&version=1.0.0&LAYER=img&tileMatrixSet=w&TileMatrix={z}&TileRow={y}&TileCol={x}&style=default&format=tiles&tk=${token}`,
        subdomains: ['0','1','2','3','4','5','6','7'],
        maximumLevel: 18
    }),
    baseLayerPicker: false,
    geocoder: false,
    // 关键: 不用 Cesium Ion
});
Cesium.Ion.defaultAccessToken = '';  // ← 显式清空,免得偷偷用它
```

### 10. GeoJSON 文件太大,加载 10 秒

**症状**:省级边界 GeoJSON 8MB,网络请求 + 解析 10 秒,期间地图空白。
**解决**:
- **方案 A:简化几何** (mapshaper / topojson)
```bash
mapshaper china.json -simplify 20% -o china_simple.json
# 8MB → 800KB
```
- **方案 B:只加载当前可视区域**
```js
async function loadVisibleProvinces(viewport) {
    const visible = provinceList.filter(p => isInViewport(p, viewport));
    const geojsons = await Promise.all(visible.map(p => fetch(`/geojson/${p.code}.json`).then(r => r.json())));
    viewer.dataSources.add(Cesium.GeoJsonDataSource.load(geojsons));
}
```

### 11. 瓦片 404 不报错,静默白屏

**症状**:天地图瓦片路径错一位,viewer 显示白屏,控制台没 error。
**根因**:Cesium 对 404 静默处理。
**解决**:
```js
viewer.scene.imageryLayers.get(0).errorEvent.addEventListener((err) => {
    console.error('瓦片加载失败:', err);
    // 上报到后端
    fetch('/api/log/tile-error', { method: 'POST', body: JSON.stringify(err) });
});
```

### 12. Cesium 内存泄漏,30 分钟卡死

**症状**:长时间运行(2h+),浏览器内存从 500MB → 3GB,卡死。
**根因**:Entity / DataSource / Primitive 没销毁。
**解决**:
```js
// 每次更新前清
function clearAll() {
    viewer.entities.removeAll();
    viewer.dataSources.removeAll();
    viewer.scene.primitives.removeAll();
    viewer.scene.requestRender();  // 关键:通知场景重绘
}
// 或:用 viewer.scene.primitives.add 后保留 handle,删除时 remove(handle)
```

---

## 三、配置 / 安全相关(3 个)

### 13. token 在 config 里被覆盖成掩码

**症状**:"前几天还好的"token 今天突然不工作,看 config.json 发现 token 变成了 `***abc`。
**根因**:
1. 后端 `/api/config` 返配置时把 token mask 了(安全考虑)
2. 前端拿到后填回表单
3. 用户保存 → mask 写回 config
**根因**:
- 三层防御:
  1. **后端永远返 `***abc`**:前端永远拿不到真值
  2. **前端 placeholder 模式**:input 是 placeholder="***abc" 显示,不填值,真值留原状
  3. **服务端守卫**:保存时检测值是不是掩码形式(`***xxx`),是则跳过不写
```python
def is_masked(value: str) -> bool:
    return bool(value) and value.startswith('***')

def update_field(key: str, new_value: str, old_value: str):
    if is_masked(new_value):
        # 掩码值,不写,保留 old_value
        return old_value
    return new_value
```

### 14. Python venv 跨电脑爆炸

**症状**:家里电脑跑得好好的项目,拷贝到单位电脑,启动报 `ModuleNotFoundError: No module named 'cryptography'`,但 `.\.venv\Scripts\python.exe -c "import cryptography"` 单跑又正常。
**根因**:`pyvenv.cfg` 里 `home = C:\Users\家里\...\.venv\...` 还指旧电脑路径,新电脑的 venv 是个"幽灵"。
**解决**:
```python
# scripts/check_venv.py
import sys, subprocess
from pathlib import Path

def check():
    pyvenv_cfg = Path(".venv/pyvenv.cfg")
    if not pyvenv_cfg.exists():
        return 0  # 没 venv,正常
    cfg = pyvenv_cfg.read_text(encoding="utf-8")
    # 关键检查:home 路径在当前电脑存在?
    for line in cfg.splitlines():
        if line.startswith("home = "):
            home = line.split("=", 1)[1].strip()
            if not Path(home).exists():
                print(f"❌ venv home 路径不存在: {home}")
                return 1
    # 试跑核心包
    for pkg in ["fastapi", "uvicorn", "cryptography"]:
        r = subprocess.run([sys.executable, "-c", f"import {pkg}"], capture_output=True)
        if r.returncode != 0:
            print(f"❌ {pkg} 不可用")
            return 1
    return 0

if __name__ == "__main__":
    sys.exit(check())
```
**接入启动脚本**:
```bat
@echo off
.\.venv\Scripts\python.exe scripts\check_venv.py --check
if errorlevel 1 (
    echo [ERROR] venv 损坏,删除重建
    rmdir /s /q .venv
    python -m venv .venv
    .\.venv\Scripts\pip.exe install -r requirements.txt
)
.\.venv\Scripts\pythonw.exe app.py
```

### 15. config.json 被改坏,服务起不来

**症状**:用户手改了 config.json,JSON 格式错(多一个逗号),服务起不来。
**解决 — auto backup + hash 校验**:
```python
# config_store.py
import shutil, hashlib
from pathlib import Path

def save_config(data: dict, path: Path):
    # 1. 备份
    if path.exists():
        shutil.copy2(path, path.with_suffix(".bak"))
    # 2. 写新
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    # 3. 写 hash
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_suffix(".sha256").write_text(h, encoding="utf-8")

def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    # hash 校验
    sha_path = path.with_suffix(".sha256")
    if sha_path.exists():
        expected = sha_path.read_text(encoding="utf-8").strip()
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected != actual:
            # 损坏,从 .bak 回滚
            bak = path.with_suffix(".bak")
            if bak.exists():
                shutil.copy2(bak, path)
                print("[WARN] config 损坏,已从 .bak 回滚")
    return json.loads(path.read_text(encoding="utf-8"))
```

---

## 四、性能 / 兼容相关(3 个)

### 16. CSS @import 跨域失败,样式丢失

**症状**:本地样式都正常,部署到 nginx 之后某个子页样式丢了。
**根因**:`<style>@import url('https://other-domain.com/x.css');</style>` 跨域被浏览器拦。
**解决**:
- 全部用 `<link rel="stylesheet" href="...">` 标签
- 不要用 `@import`(除了 SCSS/Less 编译期)

### 17. 大屏 dashboard 底边框"差一点点"

**症状**:用户连续说"底部边框线没出来 / 差一点点",我每次都改 offset,总差。
**根因**:用户视觉误差,"差一点点"实际是"border 太细 + 离底太近"。
**解决**:**加粗 + 上提**,变成 inset shadow
```css
/* 之前的: 1px border-bottom */
.tab-dashboard {
    border-bottom: 1px solid rgba(96, 165, 250, 0.5);
}
/* 改成: 3px inset shadow,offset -4px 往上提 */
.tab-dashboard.active {
    box-shadow: inset 0 -4px 0 0 rgba(96, 165, 250, 0.85);
}
```
**教训**:用户说"差一点点"通常意味着"**视觉差异够大才满足**",小改没用。

### 18. 深色背景灰字看不清

**症状**:暗色主题,参数区文字用 `text-gray-400`(slate-400 = #94a3b8),用户说"看不清"。
**根因**:slate-400 在深色背景(slate-900)上对比度只有 4.0:1,低于 WCAG AA 4.5:1。
**解决 — 硬性规则**:深色背景正文必须 `slate-200` (#e2e8f0) 及以上
```css
/* ❌ 错 */
.dark .param { color: #94a3b8; }
/* ✅ 对 */
.dark .param { color: #e2e8f0; }
/* ✅ 代码片段 */
.dark .code-snippet {
    background: rgba(96, 165, 250, 0.18);
    color: #bfdbfe;
}
```
**对照表**:
- `#94a3b8` (slate-400) ❌
- `#cbd5e1` (slate-300) ⚠️ 勉强
- `#e2e8f0` (slate-200) ✅ 主文字
- `#f1f5f9` (slate-100) ✅ 标题
- `#bfdbfe` (blue-200) ✅ 代码

---

## 避坑口诀(2026-08)

**F5 清 / token 掩 / 跨电脑 venv / Cesium 不清空 / SSE 不 buffer / 深色 ≥ slate-200 / 持久化 IndexedDB / 二次开发先 mockup**
