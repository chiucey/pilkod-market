# 示例 · 深圳投标可视化

本文件给出一个基于**真实抓取数据**的完整可用示例：深圳市龙岗区「院容院貌提升改造工程」（招标项目编号 4403942026081200201Y），2026-08-14 发布招标公告，2026-08-28 公示中标结果。

数据来源：`tender-server` 的 `project_progress` 与 `get_notice` 实际返回。

---

## 示例 1：流程时间轴（kind="diagram"，8 个阶段，无 Chart.js）

适用配方 A。8 个阶段点属于流程视图而非分析图表，用 CSS/SVG 轨道渲染，不引入 Chart.js。

```html
<mavis-widget
 version="mavis.widget.v1"
  kind="diagram"
  title="院容院貌提升改造工程 · 全流程进度"
  height="420"
  min-height="300"
  max-height="640"
  streaming="html-first"
  capabilities="resize,sendPrompt"
  theme="app"
  token-set="mavis.semantic.v1">
  <mavis-meta type="json">{"summary":"院容院貌提升改造工程已于 2026-08-28 公示中标，深圳市华懋建设工程有限公司中标 177.249273 万元，全流程 8 个阶段公告齐全。","dataSource":"深圳公共资源交易网 szggzy.com 公告详情（project_progress 返回）","chartType":"timeline","datasetShape":{"rows":8,"dimensions":["stage","noticeType","releaseTime"],"measures":[]},"interactions":[{"id":"inspect-step","label":"核对该阶段公告","capability":"sendPrompt"}]}</mavis-meta>
  <mavis-style>
    body{margin:0;padding:16px;background:var(--mw-bg);color:var(--mw-text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:14px}
    .sum{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:6px}
    .badge{font-size:12px;font-weight:500;border-radius:999px;padding:3px 11px;border:1px solid var(--mw-border)}
    .badge.done{color:var(--mw-success);border-color:var(--mw-success)}
    .badge.warn{color:var(--mw-warning);border-color:var(--mw-warning)}
    .muted{color:var(--mw-text-muted)}
    .meta{font-size:12px;color:var(--mw-text-subtle);margin:0 0 14px}
    .track{display:flex;gap:0;overflow-x:auto;padding:4px 0 12px}
    .node{flex:1 1 0;min-width:78px;text-align:center;position:relative}
    .dot{width:13px;height:13px;border-radius:50%;margin:0 auto 7px;background:var(--mw-surface-muted);border:2px solid var(--mw-border)}
    .node.on .dot{background:var(--mw-accent);border-color:var(--mw-accent)}
    .bar{height:2px;background:var(--mw-border);margin:-16px 0 8px}
    .node.on .bar{background:var(--mw-accent)}
    .nlab{font-size:12px;color:var(--mw-text-muted);display:block}
    .node.on .nlab{color:var(--mw-text)}
    .list{border-top:1px solid var(--mw-border);padding-top:10px}
    .row{display:flex;gap:10px;align-items:baseline;padding:7px 8px;border-radius:8px;cursor:pointer;transition:background .15s}
    .row:hover{background:var(--mw-surface-muted)}
    .row.dim{opacity:.35}
    .row .st{font-size:12px;color:var(--mw-text-muted);flex:0 0 84px}
    .row .nt{flex:1;font-size:13px}
    .row .tm{font-size:12px;color:var(--mw-text-subtle);flex:0 0 auto}
    .empty{padding:22px;text-align:center;color:var(--mw-text-muted);font-size:13px}
  </mavis-style>
  <mavis-html>
    <div class="sum">
      <span class="badge done" id="cur">当前阶段：已中标</span>
      <span class="badge done">已截标</span>
      <span class="badge done">已进入评标</span>
      <span class="muted">深圳市龙岗区 · 4403942026081200201Y</span>
    </div>
    <p class="meta">院容院貌提升改造工程 · 全流程 8 个阶段公告齐全 · 数据抓取时点 2026-11-02 09:00</p>
    <div class="track" id="track"></div>
    <div class="list" id="list"></div>
  </mavis-html>
  <mavis-data name="main" type="json">[{"stage":"投标中","noticeType":"招标公告","releaseTime":"2026-08-14 09:00:05","contentId":20576627,"url":"https://www.szggzy.com/jygg/details.html?contentId=20576627"},{"stage":"投标中","noticeType":"最高投标限价公示","releaseTime":"2026-08-14 17:47:13","contentId":20578739,"url":"https://www.szggzy.com/jygg/details.html?contentId=20578739"},{"stage":"已开标","noticeType":"开标情况公示","releaseTime":"2026-08-21 11:42:01","contentId":20591270,"url":"https://www.szggzy.com/jygg/details.html?contentId=20591270"},{"stage":"评标中","noticeType":"资审及业绩公示","releaseTime":"2026-08-21 11:22:51","contentId":20591225,"url":"https://www.szggzy.com/jygg/details.html?contentId=20591225"},{"stage":"评标完成","noticeType":"评标报告公示","releaseTime":"2026-08-26 16:11:50","contentId":20600302,"url":"https://www.szggzy.com/jygg/details.html?contentId=20600302"},{"stage":"评标中","noticeType":"评标委员会公示","releaseTime":"2026-08-26 16:11:50","contentId":20600305,"url":"https://www.szggzy.com/jygg/details.html?contentId=20600305"},{"stage":"已定标","noticeType":"定标结果公示","releaseTime":"2026-08-28 15:13:37","contentId":20605054,"url":"https://www.szggzy.com/jygg/details.html?contentId=20605054"},{"stage":"已中标","noticeType":"中标结果公示","releaseTime":"2026-08-28 15:25:01","contentId":20605131,"url":"https://www.szggzy.com/jygg/details.html?contentId=20605131"}]</mavis-data>
  <mavis-script>
    (function(){
      var rows = window.__mavisData['main'] || [];
      var ORDER = ['投标中','已截标','已开标','评标中','评标完成','已定标','已中标'];
      var reached = {};
      rows.forEach(function(r){ reached[r.stage] = true; });
      var track = document.getElementById('track');
      var list = document.getElementById('list');
      if (!rows.length) { list.innerHTML = '<div class="empty">该项目暂无阶段公告</div>'; return; }
      var html = '';
      ORDER.forEach(function(st, i){
        html += '<div class="node' + (reached[st] ? ' on' : '') + '" data-stage="' + st + '">';
        if (i < ORDER.length - 1) html += '<div class="bar"></div>';
        html += '<div class="dot"></div><span class="nlab">' + st + '</span></div>';
      });
      track.innerHTML = html;
      var lh = '';
      rows.slice().sort(function(a,b){ return String(a.releaseTime).localeCompare(String(b.releaseTime)); }).forEach(function(r){
        lh += '<div class="row" data-stage="' + r.stage + '" data-cid="' + r.contentId + '" data-url="' + r.url + '">';
        lh += '<span class="st">' + r.stage + '</span>';
        lh += '<span class="nt">' + r.noticeType + '</span>';
        lh += '<span class="tm">' + r.releaseTime.slice(0,16) + '</span></div>';
      });
      list.innerHTML = lh;
      function focus(st){
        Array.prototype.forEach.call(list.querySelectorAll('.row'), function(el){
          el.classList.toggle('dim', st !== null && el.getAttribute('data-stage') !== st);
        });
      }
      Array.prototype.forEach.call(track.querySelectorAll('.node'), function(n){
        n.addEventListener('click', function(){
          var st = n.getAttribute('data-stage');
          focus(focus.current === st ? null : st);
          focus.current = focus.current === st ? null : st;
        });
      });
      list.addEventListener('click', function(ev){
        var row = ev.target.closest('.row');
        if (!row || !window.mavis || !window.mavis.sendPrompt) return;
        var cid = row.getAttribute('data-cid');
        window.mavis.sendPrompt(
          '核对「院容院貌提升改造工程」' + row.querySelector('.nt').textContent + ' 这条公告的完整内容。',
          {widgetTitle:'院容院貌提升改造工程 · 全流程进度',action:'inspect-step',selectedData:{contentId:Number(cid),stage:row.getAttribute('data-stage'),url:row.getAttribute('data-url')},visibleFilters:{},userIntent:'核对该阶段公告内容'}
        );
      });
    })();
  </mavis-script>
  <mavis-fallback>院容院貌提升改造工程（4403942026081200201Y）已于 2026-08-28 公示中标，深圳市华懋建设工程有限公司中标 177.249273 万元，工期 100 天。

全流程 8 个阶段公告：

- 2026-08-14 09:00 招标公告
- 2026-08-14 17:47 最高投标限价公示
- 2026-08-21 11:22 资审及业绩公示
- 2026-08-21 11:42 开标情况公示
- 2026-08-26 16:11 评标委员会公示
- 2026-08-26 16:11 评标报告公示
- 2026-08-28 15:13 定标结果公示
- 2026-08-28 15:25 中标结果公示

当前阶段：已中标；已截标；已进入评标。</mavis-fallback>
</mavis-widget>
```

---

## 示例 2：报价升序排列与中标定位（kind="chart"，39 个投标人，用 Chart.js）

适用配方 B。39 个投标人远超 6 个可比数据点门槛，因此用 Chart.js 横向条形图。

**排序规则：报价一律按从低到高（升序）排列**，第 1 位在最上方。这是投标人的标准视角——先看对手底价，再看自己的报价落在第几位。脚本里必须显式 `sort`，不依赖数据源原始顺序。

真实数据来源：开标情况记录表 PDF（开标情况记录表_1764078894.pdf，2026-08-21 11:30 开标，39 家投标）+ 最高投标限价公示（最高限价 189.223963 万元，投标价上限 181.114144 万元，净下浮 5%）+ 中标结果公示（中标价 177.249273 万元，定标方式直接票决）。

**这张图讲了一个反直觉的事实**：中标单位报价 177.249273 万元，在 39 家里升序排第 19 位——既不是最低也不是最高。它靠定标投票 7 票赢的。所以报价排序必须结合定标方式一起看，不能简单认为「最低价中标」。

```html
<mavis-widget
 version="mavis.widget.v1"
  kind="chart"
  title="院容院貌提升改造工程 · 投标报价升序排列（39 家）"
  height="640"
  min-height="440"
  max-height="900"
  streaming="html-first"
  capabilities="resize,sendPrompt"
  theme="app"
  token-set="mavis.semantic.v1">
  <mavis-meta type="json">{"summary": "39 家投标报价升序排列，最低 164.278522 万元、最高 180.742469 万元；中标单位深圳市华懋建设工程有限公司 177.249273 万元列第 19 位，靠定标投票 7 票中标而非低价。", "dataSource": "开标情况记录表 PDF、最高投标限价公示、中标结果公示（均取自深圳公共资源交易网真实公告）", "chartType": "bar", "datasetShape": {"rows": 39, "dimensions": ["bidder", "rank"], "measures": ["priceWan", "belowCapPct"]}, "interactions": [{"id": "review-bidder", "label": "复盘该投标人的报价与中标格局", "capability": "sendPrompt"}]}</mavis-meta>
  <mavis-style>
    body{margin:0;padding:16px;background:var(--mw-bg);color:var(--mw-text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:14px}
    .kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
    .kpi{background:var(--mw-surface);border:1px solid var(--mw-border);border-radius:10px;padding:12px}
    .kpi-label{font-size:12px;color:var(--mw-text-muted)}
    .kpi-value{font-size:20px;font-weight:700;color:var(--mw-text);margin-top:3px}
    .kpi-note{font-size:12px;color:var(--mw-text-subtle);margin-top:2px}
    .card{background:var(--mw-surface);border:1px solid var(--mw-border);border-radius:10px;padding:14px}
    .legend{display:flex;gap:14px;font-size:12px;color:var(--mw-text-muted);margin-bottom:8px;flex-wrap:wrap}
    .legend-item{display:flex;align-items:center;gap:5px}
    .legend-dot{width:10px;height:10px;border-radius:3px}
    .chart-wrap{position:relative;width:100%;height:500px}
    .note{font-size:12px;color:var(--mw-text-muted);margin-top:10px;line-height:1.6}
    .empty{padding:22px;text-align:center;color:var(--mw-text-muted);font-size:13px}
  </mavis-style>
  <mavis-html>
    <div class="kpi-row">
      <div class="kpi"><div class="kpi-label">投标家数</div><div class="kpi-value">39</div><div class="kpi-note">开标记录表实数</div></div>
      <div class="kpi"><div class="kpi-label">最低报价</div><div class="kpi-value">164.2785 万</div><div class="kpi-note">深圳市新峰建设工程</div></div>
      <div class="kpi"><div class="kpi-label">投标价上限</div><div class="kpi-value">181.1141 万</div><div class="kpi-note">限价 189.2240 万 净下浮 5%</div></div>
      <div class="kpi"><div class="kpi-label">中标价 · 升序第 19 位</div><div class="kpi-value">177.2493 万</div><div class="kpi-note">较上限下浮 2.13%</div></div>
    </div>
    <div class="card">
      <div class="legend">
        <span class="legend-item"><span class="legend-dot" style="background:var(--mw-chart-1);"></span>中标单位</span>
        <span class="legend-item"><span class="legend-dot" style="background:var(--mw-chart-2);"></span>其他投标人</span>
        <span class="legend-item">报价从低到高排列，第 1 位在最上方</span>
      </div>
      <div class="chart-wrap"><canvas id="bid-chart"></canvas></div>
      <p class="note">中标单位报价在升序中列第 19 位，并非最低价；该项目定标方式为直接票决，中标单位以 7 票胜出。低价未必中标，需结合定标方式判断。</p>
    </div>
  </mavis-html>
  <mavis-data name="main" type="json">[{"rank": 1, "bidder": "深圳市新峰建设工程有限公司", "priceWan": 164.278522, "belowCapPct": 9.3, "isWinner": false},{"rank": 2, "bidder": "深圳市凯业建设工程有限责任公司", "priceWan": 167.723484, "belowCapPct": 7.39, "isWinner": false},{"rank": 3, "bidder": "深圳市特建建设工程有限公司", "priceWan": 168.76825, "belowCapPct": 6.82, "isWinner": false},{"rank": 4, "bidder": "深圳市广发建筑工程有限公司", "priceWan": 169.06963, "belowCapPct": 6.65, "isWinner": false},{"rank": 5, "bidder": "深圳大业建设实业有限公司", "priceWan": 170.662817, "belowCapPct": 5.77, "isWinner": false},{"rank": 6, "bidder": "深圳建兆建设工程有限公司", "priceWan": 171.475812, "belowCapPct": 5.32, "isWinner": false},{"rank": 7, "bidder": "深圳市建远建设集团有限公司", "priceWan": 171.90139, "belowCapPct": 5.09, "isWinner": false},{"rank": 8, "bidder": "深圳市兴远工程有限公司", "priceWan": 172.016711, "belowCapPct": 5.02, "isWinner": false},{"rank": 9, "bidder": "深圳市中鹏建设集团有限公司", "priceWan": 172.436639, "belowCapPct": 4.79, "isWinner": false},{"rank": 10, "bidder": "深圳市华发展建设工程股份有限公司", "priceWan": 173.010428, "belowCapPct": 4.47, "isWinner": false},{"rank": 11, "bidder": "深圳市交运工程集团有限公司", "priceWan": 173.777217, "belowCapPct": 4.05, "isWinner": false},{"rank": 12, "bidder": "深圳市星中恒建筑工程有限公司", "priceWan": 175.410962, "belowCapPct": 3.15, "isWinner": false},{"rank": 13, "bidder": "深圳市名鹏建筑工程有限公司", "priceWan": 175.469542, "belowCapPct": 3.12, "isWinner": false},{"rank": 14, "bidder": "中城交建（深圳）建设有限公司", "priceWan": 175.599428, "belowCapPct": 3.04, "isWinner": false},{"rank": 15, "bidder": "深圳市名胜建设有限公司", "priceWan": 175.64805, "belowCapPct": 3.02, "isWinner": false},{"rank": 16, "bidder": "中建港湾建设（深圳）有限公司", "priceWan": 175.721165, "belowCapPct": 2.98, "isWinner": false},{"rank": 17, "bidder": "深圳市华鹏工程建设有限公司", "priceWan": 176.361649, "belowCapPct": 2.62, "isWinner": false},{"rank": 18, "bidder": "深圳大运建工有限公司", "priceWan": 176.49655, "belowCapPct": 2.55, "isWinner": false},{"rank": 19, "bidder": "深圳市华懋建设工程有限公司", "priceWan": 177.249273, "belowCapPct": 2.13, "isWinner": true},{"rank": 20, "bidder": "深圳市坚胜建设工程有限公司", "priceWan": 177.480784, "belowCapPct": 2.01, "isWinner": false},{"rank": 21, "bidder": "深圳市坤盛达建设工程有限公司", "priceWan": 177.610432, "belowCapPct": 1.93, "isWinner": false},{"rank": 22, "bidder": "深圳市诚宇建设集团有限公司", "priceWan": 178.113517, "belowCapPct": 1.66, "isWinner": false},{"rank": 23, "bidder": "深圳市永恒建设工程有限公司", "priceWan": 178.306856, "belowCapPct": 1.55, "isWinner": false},{"rank": 24, "bidder": "深圳市弘浩建设工程有限公司", "priceWan": 178.381914, "belowCapPct": 1.51, "isWinner": false},{"rank": 25, "bidder": "深圳市天翊建设有限公司", "priceWan": 178.485426, "belowCapPct": 1.45, "isWinner": false},{"rank": 26, "bidder": "深圳市中恒达建筑工程有限公司", "priceWan": 178.584259, "belowCapPct": 1.4, "isWinner": false},{"rank": 27, "bidder": "深圳市宝华建设工程有限公司", "priceWan": 178.874779, "belowCapPct": 1.24, "isWinner": false},{"rank": 28, "bidder": "深圳市中凯丰建设工程有限公司", "priceWan": 178.989557, "belowCapPct": 1.17, "isWinner": false},{"rank": 29, "bidder": "广东誉杰建筑工程有限公司", "priceWan": 179.02691, "belowCapPct": 1.15, "isWinner": false},{"rank": 30, "bidder": "深圳市忠德市政工程有限公司", "priceWan": 179.794684, "belowCapPct": 0.73, "isWinner": false},{"rank": 31, "bidder": "深圳鹏合工程有限公司", "priceWan": 179.795888, "belowCapPct": 0.73, "isWinner": false},{"rank": 32, "bidder": "深圳市品尚工程有限公司", "priceWan": 179.860102, "belowCapPct": 0.69, "isWinner": false},{"rank": 33, "bidder": "深圳市华胜建设集团有限公司", "priceWan": 179.946593, "belowCapPct": 0.64, "isWinner": false},{"rank": 34, "bidder": "深圳凯林建设工程有限公司", "priceWan": 180.141041, "belowCapPct": 0.54, "isWinner": false},{"rank": 35, "bidder": "深圳中茂工程有限公司", "priceWan": 180.302855, "belowCapPct": 0.45, "isWinner": false},{"rank": 36, "bidder": "深圳市中骏城建设有限公司", "priceWan": 180.432256, "belowCapPct": 0.38, "isWinner": false},{"rank": 37, "bidder": "深圳市安达业建设集团有限公司", "priceWan": 180.492079, "belowCapPct": 0.34, "isWinner": false},{"rank": 38, "bidder": "深圳市永朝建设工程有限公司", "priceWan": 180.732491, "belowCapPct": 0.21, "isWinner": false},{"rank": 39, "bidder": "深圳市焕升建筑集团有限公司", "priceWan": 180.742469, "belowCapPct": 0.21, "isWinner": false}]</mavis-data>
  <mavis-script>
    (function(){
      var rows = (window.__mavisData['main'] || []).slice();
      var t = window.mavisTheme.tokens;
      var fmt = new Intl.NumberFormat('zh-CN',{minimumFractionDigits:2, maximumFractionDigits:4});
      rows.sort(function(a,b){ return a.priceWan - b.priceWan; });
      var valid = rows.filter(function(r){ return typeof r.priceWan === 'number'; });
      if (!valid.length) { document.querySelector('.card').innerHTML = '<div class="empty">公告未披露各投标人报价</div>'; return; }
      var CAP = 181.114144;
      var onPick = function(r){
        if (!r || !window.mavis || !window.mavis.sendPrompt) return;
        window.mavis.sendPrompt(
          '复盘「院容院貌提升改造工程」中投标人 ' + r.bidder + ' 的报价与中标格局。该单位报价 ' + fmt.format(r.priceWan) + ' 万元，在 ' + valid.length + ' 家中按升序排第 ' + r.rank + ' 位。',
          {widgetTitle:'院容院貌提升改造工程 · 投标报价升序排列',action:'review-bidder',selectedData:{bidder:r.bidder,rank:r.rank,priceWan:r.priceWan,belowCapPct:r.belowCapPct,isWinner:!!r.isWinner,bidderCount:valid.length,priceCap:CAP},visibleFilters:{sort:'priceWan:asc'},userIntent:'复盘该投标人的报价与中标格局'}
        );
      };
      var chart = new Chart(document.getElementById('bid-chart'), {
        type: 'bar',
        data: {
          labels: valid.map(function(r){ return r.rank + '. ' + r.bidder; }),
          datasets: [{
            data: valid.map(function(r){ return r.priceWan; }),
            backgroundColor: valid.map(function(r){ return r.isWinner ? t.chart1 + 'cc' : t.chart2 + 'cc'; }),
            borderColor: valid.map(function(r){ return r.isWinner ? t.chart1 : t.chart2; }),
            borderWidth: 1.5,
            borderRadius: 4
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: t.surface, titleColor: t.text, bodyColor: t.textMuted, borderColor: t.border, borderWidth: 1,
              callbacks: { label: function(c){ return fmt.format(c.parsed.x) + ' 万元（较上限下浮 ' + valid[c.dataIndex].belowCapPct.toFixed(2) + '%）'; } } }
          },
          scales: {
            x: { grid: { color: t.chartGrid }, ticks: { color: t.chartAxis, callback: function(v){ return v.toFixed(0) + ' 万'; } } },
            y: { grid: { display: false }, ticks: { color: t.chartAxis, font: { size: 10 }, autoSkip: false } }
          },
          animation: { duration: 600, easing: 'easeOutQuart' }
        },
        onClick: function(evt, elements){
          if (!elements.length) return;
          onPick(valid[elements[0].index]);
        }
      });
      var wrap = document.querySelector('.card');
      wrap.style.cursor = 'pointer';
      wrap.addEventListener('click', function(){
        onPick(valid[0]);
      });
      window.addEventListener('mavis:theme-change', function(){
        var nt = window.mavisTheme.tokens;
        chart.data.datasets[0].backgroundColor = valid.map(function(r){ return r.isWinner ? nt.chart1 + 'cc' : nt.chart2 + 'cc'; });
        chart.data.datasets[0].borderColor = valid.map(function(r){ return r.isWinner ? nt.chart1 : nt.chart2; });
        chart.options.scales.x.ticks.color = nt.chartAxis;
        chart.options.scales.x.grid.color = nt.chartGrid;
        chart.options.scales.y.ticks.color = nt.chartAxis;
        chart.options.plugins.tooltip.backgroundColor = nt.surface;
        chart.options.plugins.tooltip.titleColor = nt.text;
        chart.options.plugins.tooltip.bodyColor = nt.textMuted;
        chart.options.plugins.tooltip.borderColor = nt.border;
        chart.update('none');
      });
    })();
  </mavis-script>
  <mavis-fallback>院容院貌提升改造工程（4403942026081200201Y001）共 39 家投标，报价按从低到高排列。

最低 12 名：

| 升序 | 投标人 | 报价（万元） | 较上限下浮 |
| --- | --- | --- | --- |
| 1 | 深圳市新峰建设工程有限公司 | 164.2785 | 9.30% |
| 2 | 深圳市凯业建设工程有限责任公司 | 167.7235 | 7.39% |
| 3 | 深圳市特建建设工程有限公司 | 168.7682 | 6.82% |
| 4 | 深圳市广发建筑工程有限公司 | 169.0696 | 6.65% |
| 5 | 深圳大业建设实业有限公司 | 170.6628 | 5.77% |
| 6 | 深圳建兆建设工程有限公司 | 171.4758 | 5.32% |
| 7 | 深圳市建远建设集团有限公司 | 171.9014 | 5.09% |
| 8 | 深圳市兴远工程有限公司 | 172.0167 | 5.02% |
| 9 | 深圳市中鹏建设集团有限公司 | 172.4366 | 4.79% |
| 10 | 深圳市华发展建设工程股份有限公司 | 173.0104 | 4.47% |
| 11 | 深圳市交运工程集团有限公司 | 173.7772 | 4.05% |
| 12 | 深圳市星中恒建筑工程有限公司 | 175.4110 | 3.15% |

最高 3 名：

| 升序 | 投标人 | 报价（万元） | 较上限下浮 |
| --- | --- | --- | --- |
| 37 | 深圳市安达业建设集团有限公司 | 180.4921 | 0.34% |
| 38 | 深圳市永朝建设工程有限公司 | 180.7325 | 0.21% |
| 39 | 深圳市焕升建筑集团有限公司 | 180.7425 | 0.21% |

报价区间 164.278522 ~ 180.742469 万元，中位数 177.480784 万元。投标价上限 181.114144 万元（最高投标限价 189.223963 万元，净下浮 5%）。中标单位深圳市华懋建设工程有限公司报价 177.249273 万元，升序第 19 位，较上限下浮 2.13%——并非最低价；该项目定标方式为直接票决，中标单位以 7 票胜出。</mavis-fallback>
</mavis-widget>
```

---

## 示例 3：资料获取状态（kind="dashboard"）

适用配方 C。dashboard 必须用 `capabilities="resize,sendPrompt"`，并配至少两个可点元素与对应处理器。

```html
<mavis-widget
 version="mavis.widget.v1"
  kind="dashboard"
  title="院容院貌提升改造工程 · 评标资料获取状态"
  height="560"
  min-height="400"
  max-height="900"
  streaming="html-first"
  capabilities="resize,sendPrompt"
  theme="app"
  token-set="mavis.semantic.v1">
  <mavis-meta type="json">{"summary":"评标报告与开标记录表均已自动下载，共 2 份 906 KB；该公告无中标结果公告 PDF，中标信息在正文内。","dataSource":"download_docs 与 get_notice 实际返回","chartType":"dashboard","datasetShape":{"rows":4,"dimensions":["docClass","downloaded"],"measures":["bytes"]},"interactions":[{"id":"parse-doc","label":"解析已下载文件","capability":"sendPrompt"},{"id":"manual-guide","label":"生成人工下载指引","capability":"sendPrompt"}]}</mavis-meta>
  <mavis-style>
    body{margin:0;padding:16px;background:var(--mw-bg);color:var(--mw-text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:14px}
    .kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
    .kpi{background:var(--mw-surface);border:1px solid var(--mw-border);border-radius:10px;padding:12px}
    .kpi-label{font-size:12px;color:var(--mw-text-muted)}
    .kpi-value{font-size:20px;font-weight:700;color:var(--mw-text);margin-top:3px}
    .card{background:var(--mw-surface);border:1px solid var(--mw-border);border-radius:10px;padding:14px}
    table{width:100%;border-collapse:collapse}
    th{text-align:left;padding:8px 10px;font-size:12px;font-weight:500;color:var(--mw-text-muted);background:var(--mw-surface-muted);border-bottom:1px solid var(--mw-border)}
    td{padding:9px 10px;border-bottom:1px solid var(--mw-border);font-size:13px}
    tr:last-child td{border-bottom:none}
    .st-ok{color:var(--mw-success)}
    .st-manual{color:var(--mw-warning)}
    .st-none{color:var(--mw-text-subtle)}
    .row{cursor:pointer}
    .row:hover td{background:var(--mw-surface-muted)}
    .action-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;padding-top:12px;border-top:1px solid var(--mw-border)}
    .action-btn{padding:6px 12px;border-radius:8px;border:1px solid var(--mw-border);background:var(--mw-surface);color:var(--mw-text-muted);font-size:12px;cursor:pointer;font-family:inherit}
    .action-btn:hover{border-color:var(--mw-accent);color:var(--mw-accent)}
    .empty{padding:22px;text-align:center;color:var(--mw-text-muted);font-size:13px}
  </mavis-style>
  <mavis-html>
    <div class="kpi-row">
      <div class="kpi"><div class="kpi-label">附件总数</div><div class="kpi-value">4</div></div>
      <div class="kpi"><div class="kpi-label">已自动下载</div><div class="kpi-value" id="k-dl">2</div></div>
      <div class="kpi"><div class="kpi-label">需人工下载</div><div class="kpi-value" id="k-man">0</div></div>
      <div class="kpi"><div class="kpi-label">已下载体积</div><div class="kpi-value" id="k-size">0.89 MB</div></div>
    </div>
    <div class="card">
      <table>
        <thead><tr><th>文件名</th><th>用途</th><th>状态</th><th>体积</th></tr></thead>
        <tbody id="tb"></tbody>
      </table>
      <div class="action-bar">
        <button class="action-btn" data-action="parse-doc">解析已下载文件</button>
        <button class="action-btn" data-action="manual-guide">生成人工下载指引</button>
      </div>
    </div>
  </mavis-html>
  <mavis-data name="main" type="json">[{"name":"商务组评标报告.pdf","docClass":"pingbiao","downloaded":true,"bytes":876666,"captchaProtected":false,"contentId":20600302},{"name":"开标情况记录表_1764078894.pdf","docClass":"kbreport","downloaded":true,"bytes":49376,"captchaProtected":false,"contentId":20591270},{"name":"开标一览表.pdf","docClass":"kbreport","downloaded":false,"bytes":null,"captchaProtected":false,"contentId":20605131},{"name":"评分结果表.pdf","docClass":"pingbiao","downloaded":false,"bytes":null,"captchaProtected":true,"contentId":20605131,"staticUrl":"http://zfcg.szggzy.com:8081/gsgg/002001/002001004/002001004001/20260828/example.html"}]</mavis-data>
  <mavis-script>
    (function(){
      var rows = window.__mavisData['main'] || [];
      var LABELS = {kbreport:'开标报告',pingbiao:'评标报告',zhongbiao:'中标信息',zixing:'资信/资格文件',qita:'其他'};
      var tb = document.getElementById('tb');
      if (!rows.length) { tb.innerHTML = '<tr><td colspan="4"><div class="empty">该公告没有可下载附件</div></td></tr>'; return; }
      var dl = 0, man = 0, bytes = 0, h = '';
      rows.forEach(function(r){
        if (r.downloaded) { dl++; bytes += (r.bytes || 0); }
        if (r.captchaProtected) man++;
        var st = r.downloaded ? '<span class="st-ok">已下载</span>' : (r.captchaProtected ? '<span class="st-manual">需人工下载</span>' : '<span class="st-none">未获取</span>');
        var size = r.bytes ? (r.bytes/1024/1024).toFixed(2) + ' MB' : '—';
        h += '<tr class="row" data-name="' + r.name + '" data-cid="' + r.contentId + '" data-manual="' + (r.captchaProtected ? '1' : '0') + '">';
        h += '<td>' + r.name + '</td><td>' + (LABELS[r.docClass] || r.docClass) + '</td><td>' + st + '</td><td>' + size + '</td></tr>';
      });
      tb.innerHTML = h;
      document.getElementById('k-dl').textContent = String(dl);
      document.getElementById('k-man').textContent = String(man);
      document.getElementById('k-size').textContent = (bytes/1024/1024).toFixed(2) + ' MB';
      tb.addEventListener('click', function(ev){
        var row = ev.target.closest('tr.row');
        if (!row || !window.mavis || !window.mavis.sendPrompt) return;
        var name = row.getAttribute('data-name');
        var cid = Number(row.getAttribute('data-cid'));
        var manual = row.getAttribute('data-manual') === '1';
        window.mavis.sendPrompt(
          manual
            ? '「' + name + '」受图形验证码保护，请给出人工下载步骤。'
            : '解析已下载的「' + name + '」，提炼关键数据。',
          {widgetTitle:'院容院貌提升改造工程 · 评标资料获取状态',action: manual ? 'manual-guide' : 'parse-doc',selectedData:{name:name,contentId:cid,captchaProtected:manual},visibleFilters:{},userIntent: manual ? '获取人工下载指引' : '解析已下载的评标文件'}
        );
      });
      Array.prototype.forEach.call(document.querySelectorAll('.action-btn'), function(b){
        b.addEventListener('click', function(){
          if (!window.mavis || !window.mavis.sendPrompt) return;
          var a = b.getAttribute('data-action');
          window.mavis.sendPrompt(
            a === 'parse-doc' ? '把已下载的评标报告与开标记录表提炼成投标复盘要点。' : '给出需人工下载附件的操作指引。',
            {widgetTitle:'院容院貌提升改造工程 · 评标资料获取状态',action:a,selectedData:{fileCount:rows.length},visibleFilters:{},userIntent: a === 'parse-doc' ? '提炼评标材料要点' : '获取人工下载指引'}
          );
        });
      });
    })();
  </mavis-script>
  <mavis-fallback>院容院貌提升改造工程的评标资料共 4 项，已自动下载 2 份（合计 0.89 MB）。

- 商务组评标报告.pdf — 评标报告 — 已下载（0.84 MB）
- 开标情况记录表_1764078894.pdf — 开标报告 — 已下载（0.05 MB）
- 开标一览表.pdf — 开标报告 — 未获取
- 评分结果表.pdf — 评标报告 — 需人工下载（受图形验证码保护）

建设工程板块附件可自动下载；政府采购板块附件需在公告页过验证码后人工获取。</mavis-fallback>
</mavis-widget>
```

---

## 三条示例的选型对照

| 示例 | kind | 数据点 | 渲染器 | 为什么这样选 |
| --- | --- | --- | --- |
| 1 流程时间轴 | diagram | 8 个阶段 | CSS/SVG 轨道 | 流程视图不是分析图表，不引入 Chart.js |
| 2 报价对比 | chart | 6 个投标人 | Chart.js 横向条形 | 达到 ≥6 个可比数据点门槛 |
| 3 资料状态 | dashboard | 4 项附件 | 表格 + KPI | dashboard 必须配 sendPrompt 与可点元素 |

若投标人只有 5 家或更少，示例 2 必须改用 CSS bench 条形并去掉 `new Chart(...)`；`kind` 也要相应改为 `chart` 之外的形态。
