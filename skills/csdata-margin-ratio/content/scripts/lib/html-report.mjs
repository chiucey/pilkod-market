// html-report.mjs — 生成自包含 HTML 分析报告（内嵌 plotly.js，离线可开）
import fs from 'node:fs';
import path from 'node:path';
import { fetchBuffer } from './net.mjs';

const PLOTLY_VERSION = '2.35.2';
const PLOTLY_URLS = [
  `https://unpkg.com/plotly.js-dist-min@${PLOTLY_VERSION}/plotly.min.js`,
  `https://cdn.plot.ly/plotly-${PLOTLY_VERSION}.min.js`,
  `https://cdn.jsdelivr.net/npm/plotly.js-dist-min@${PLOTLY_VERSION}/plotly.min.js`,
];

/** 拿到 plotly.js：优先本地缓存，其次下载，最后退回 CDN 引用 */
export async function resolvePlotly(cacheDir) {
  const local = path.join(cacheDir, 'plotly.min.js');
  if (fs.existsSync(local) && fs.statSync(local).size > 1_000_000) {
    return { mode: 'inline', js: fs.readFileSync(local, 'utf8') };
  }
  for (const url of PLOTLY_URLS) {
    try {
      const buf = await fetchBuffer(url, { headers: { 'Accept-Encoding': 'identity' }, timeout: 120000 });
      if (buf.length > 1_000_000) {
        fs.mkdirSync(cacheDir, { recursive: true });
        fs.writeFileSync(local, buf);
        return { mode: 'inline', js: buf.toString('utf8') };
      }
    } catch { /* 试下一个源 */ }
  }
  return { mode: 'cdn', js: null };
}

const CSS = `
  :root{--primary:#ed3030;--navy:#1e3a8a;--accent:#60a5fa;--bg:#f8fafc;--text:#1f2937;
        --grid:#e5e7eb;--card:#fff;--border:#e2e8f0;--muted:#64748b;--up:#dc2626;--down:#16a34a}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);
       font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
       font-size:14px;line-height:1.6}
  .wrap{max-width:1280px;margin:0 auto;padding:32px 24px 64px}
  header{border-bottom:2px solid var(--text);padding-bottom:18px;margin-bottom:26px}
  h1{font-family:Georgia,"Songti SC",serif;font-size:26px;margin:0 0 8px;font-weight:700}
  h1 .red{color:var(--primary)} h1 .navy{color:var(--navy)}
  .sub{color:var(--muted);font-size:13px} .sub b{color:var(--text)}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:14px;margin-bottom:28px}
  .kpi{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px;
       box-shadow:0 1px 2px rgba(15,23,42,.05);position:relative;overflow:hidden}
  .kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--accent)}
  .kpi.k-red::before{background:var(--primary)}.kpi.k-navy::before{background:var(--navy)}
  .kpi.k-blue::before{background:var(--accent)}.kpi.k-gray::before{background:#94a3b8}
  .kpi.k-amber::before{background:#f59e0b}
  .kpi-l{font-size:12px;color:var(--muted)}
  .kpi-v{font-family:Georgia,"Songti SC",serif;font-size:25px;font-weight:700;margin:2px 0 1px}
  .kpi.k-red .kpi-v{color:var(--primary)}.kpi.k-navy .kpi-v{color:var(--navy)}
  .kpi-s{font-size:11px;color:var(--muted)}
  .tag{font-size:10px;background:#eef2f7;color:var(--muted);padding:1px 6px;border-radius:4px}
  .panel{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:8px 14px 14px;
         margin-bottom:22px;box-shadow:0 1px 2px rgba(15,23,42,.05)}
  .p-head{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;
          padding:10px 2px 4px;border-bottom:1px solid var(--border);margin-bottom:6px}
  .p-title{font-family:Georgia,"Songti SC",serif;font-size:18px;font-weight:700}
  .p-note{font-size:12px;color:var(--muted)}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
  @media(max-width:900px){.grid2{grid-template-columns:1fr}}
  .legendkey{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin:8px 0 0}
  .legendkey i{display:inline-block;width:18px;height:0;border-top-width:3px;border-top-style:solid;
               vertical-align:middle;margin-right:6px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{border-bottom:1px solid var(--grid);padding:9px 10px;text-align:left}
  th{background:#f1f5f9;font-weight:600;font-size:12px;color:#334155;position:sticky;top:0}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  td.yr{font-weight:700}.up{color:var(--up)}.down{color:var(--down)}.idx{color:var(--navy)}
  .d{display:block;font-size:10px;color:var(--muted);font-weight:400}
  .tbl-wrap{max-height:440px;overflow:auto;border:1px solid var(--border);border-radius:8px}
  .tools{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:10px 0}
  input[type=search]{border:1px solid var(--border);border-radius:6px;padding:6px 10px;font-size:13px;
                      width:220px;background:#fff;color:var(--text);outline:none}
  footer{border-top:1px solid var(--border);margin-top:14px;padding-top:16px;color:var(--muted);font-size:12px}
  footer b{color:var(--text)}
  code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-size:11px}
  .disc{margin-top:8px;padding:10px 12px;background:#fff7ed;border-left:3px solid #f59e0b;
        border-radius:0 6px 6px 0;font-size:12px;color:#7c2d12}
`;

function kpi(cls, label, value, sub) {
  return `<div class="kpi ${cls}"><div class="kpi-l">${label}</div>
    <div class="kpi-v">${value}</div><div class="kpi-s">${sub}</div></div>`;
}

/** 生成 HTML 报告 */
export function buildHtml(data, { plotly, sourceNote = '' }) {
  const S = data.stats;
  const plotlyTag = plotly.mode === 'inline'
    ? `<script>${plotly.js}</script>`
    : `<script src="https://cdn.plot.ly/plotly-${PLOTLY_VERSION}.min.js" charset="utf-8"></script>`;

  const kpis = [
    kpi('k-red', `最新维持担保比例 <span class="tag">${S.end}</span>`, `${S.latest.toFixed(2)}%`,
      `较期间均值 ${(S.latest - S.mean).toFixed(2)}pp`),
    kpi('k-navy', `最新上证指数 <span class="tag">${S.end}</span>`, S.sse_latest.toFixed(2),
      `区间 ${S.sse_pct >= 0 ? '+' : ''}${S.sse_pct.toFixed(2)}%`),
    kpi('k-blue', '期间均值', `${S.mean.toFixed(2)}%`, `中位数 ${S.median.toFixed(2)}%`),
    kpi('k-red', `区间最高 <span class="tag">${S.max_date}</span>`, `${S.max.toFixed(2)}%`,
      `上证同日 ${S.sse_max.toFixed(2)}`),
    kpi('k-gray', `区间最低 <span class="tag">${S.min_date}</span>`, `${S.min.toFixed(2)}%`,
      `上证同日 ${S.sse_min.toFixed(2)}`),
    kpi('k-amber', '两序列日变化相关性', S.corr_ret.toFixed(3), `水平值相关性 ${S.corr_level.toFixed(3)}`),
  ].join('');

  const yearRows = data.years.map((y) => `<tr>
    <td class="yr">${y.year}</td><td class="num">${y.n}</td>
    <td class="num">${y.mean.toFixed(2)}%</td><td class="num">${y.last.toFixed(2)}%</td>
    <td class="num up">${y.high.toFixed(2)}%<span class="d">${y.high_date}</span></td>
    <td class="num down">${y.low.toFixed(2)}%<span class="d">${y.low_date}</span></td>
    <td class="num">${(y.last - y.first >= 0 ? '+' : '')}${(y.last - y.first).toFixed(2)}%</td>
    <td class="num idx">${y.sse_last.toFixed(2)}</td>
    <td class="num idx">${((y.sse_last / y.sse_first - 1) * 100 >= 0 ? '+' : '')}${((y.sse_last / y.sse_first - 1) * 100).toFixed(2)}%</td>
  </tr>`).join('');

  const yearCheck = data.years.map((y) => `${y.year} 年 ${y.n}`).join(' / ');

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>融资融券市场平均维持担保比例 × 上证指数分析 | ${S.start} ~ ${S.end}</title>
<style>${CSS}</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>融资融券市场 <span class="red">平均维持担保比例</span> × <span class="navy">上证指数</span> 联合分析</h1>
  <div class="sub">
    样本区间 <b>${S.start} ~ ${S.end}</b> ｜ 交易日 <b>${S.n}</b> 个 ｜
    比例来源 <b>中证数据 www.csdata.cn</b>「融资融券市场每日数据统计」/「融资融券历史数据-日度历史数据统计」文件最后一行的「平均维持担保比例」；
    指数来源 <b>搜狐财经 / 新浪财经</b> 日线收盘（双源逐日校验一致）
  </div>
</header>

<div class="kpis">${kpis}</div>

<div class="panel">
  <div class="p-head">
    <div class="p-title">每日平均维持担保比例 与 上证指数</div>
    <div class="p-note">双坐标轴：左轴＝维持担保比例(%)，右轴＝上证指数(点)</div>
  </div>
  <div id="chart_main"></div>
  <div class="legendkey">
    <span><i style="border-color:#ed3030"></i>平均维持担保比例（左轴，红，带数据点）</span>
    <span><i style="border-color:#1e3a8a"></i>上证指数（右轴，深蓝，实线无点）</span>
    <span><i style="border-color:#60a5fa;border-top-style:dashed"></i>维持担保比例线性趋势（左轴，浅蓝虚线）</span>
  </div>
  <div class="legend-note">双轴图纵坐标刻度相互独立，交叉点不代表数值相等；下方「归一化对比」以同一基准(起始日=100)呈现两者相对走势。</div>
</div>

<div class="panel">
  <div class="p-head">
    <div class="p-title">归一化对比（${S.start} ＝ 100）</div>
    <div class="p-note">消除量纲差异后，观察两者的同涨同跌</div>
  </div>
  <div id="chart_norm"></div>
  <div class="legend-note">日变化相关系数 <b>${S.corr_ret.toFixed(3)}</b>（水平值相关系数 <b>${S.corr_level.toFixed(3)}</b>）。</div>
</div>

<div class="grid2">
  <div class="panel">
    <div class="p-head"><div class="p-title">距历史高点回撤</div>
      <div class="p-note">衡量杠杆安全垫的收缩幅度</div></div>
    <div id="chart_dd"></div>
  </div>
  <div class="panel">
    <div class="p-head"><div class="p-title">月度均值与月度波动区间</div>
      <div class="p-note">红线为月均值，蓝色带为当月最高—最低区间</div></div>
    <div id="chart_month"></div>
  </div>
</div>

<div class="panel">
  <div class="p-head"><div class="p-title">年度统计</div>
    <div class="p-note">当前年度为部分年度</div></div>
  <div style="overflow:auto"><table>
    <thead><tr><th>年份</th><th class="num">交易日</th><th class="num">比例均值</th>
      <th class="num">比例期末</th><th class="num">比例年内最高</th><th class="num">比例年内最低</th>
      <th class="num">比例年内涨跌</th><th class="num">上证期末</th><th class="num">上证年内涨跌</th>
    </tr></thead><tbody>${yearRows}</tbody></table></div>
</div>

<div class="panel">
  <div class="p-head"><div class="p-title">逐日明细</div>
    <div class="p-note">共 ${S.n} 条，与 Excel 版完全一致</div></div>
  <div class="tools">
    <input type="search" id="q" placeholder="按日期筛选，如 ${S.start.slice(0, 7)}">
    <span class="p-note" id="cnt">显示 ${S.n} 条</span>
  </div>
  <div class="tbl-wrap"><table>
    <thead><tr><th style="width:58px">序号</th><th style="width:110px">交易日</th>
      <th class="num">维持担保比例(%)</th><th class="num">上证指数(收盘)</th>
      <th class="num">上证涨跌幅(%)</th><th class="num">比例较前一日(pp)</th>
      <th class="num">距比例高点(pp)</th></tr></thead>
    <tbody id="tbody"></tbody></table></div>
</div>

<footer>
  <p><b>比例数据来源</b>：中证数据（csdata.cn）「融资融券市场每日数据统计」与「融资融券历史数据 — 融资融券市场日度历史数据统计」栏目，
  逐日下载官网发布的 Excel 文件并提取最后一行的「平均维持担保比例」。</p>
  <p><b>指数数据来源</b>：搜狐财经与新浪财经历史日线（上证指数 000001），两个源逐个交易日收盘价比对，差异须小于 0.01 点。</p>
  <p><b>口径说明</b>：2024 年至 2025-02 的文件以文本形式存储百分比（如 <code>239.5%</code>），
  2025-02 起为百分比格式数值（<code>2.556273</code>），本表统一换算为「百分比数值」，即 255.6273 表示 255.6273%。</p>
  <p><b>完整性校验</b>：以交易所交易日历为基准，${yearCheck} 个交易日逐一比对，全部吻合，无缺失；
  全部 ${S.n} 个交易日的文件内统计日期与标题日期一致。</p>
  ${sourceNote}
  <div class="disc">仅供研究参考，不构成任何投资建议。</div>
</footer>
</div>

${plotlyTag}
<script>
const DATA = ${JSON.stringify(data)};
const C={primary:'#ed3030',navy:'#1e3a8a',accent:'#60a5fa',background:'#f8fafc',text:'#1f2937',grid:'#e5e7eb'};
const AX={showgrid:true,gridwidth:1,gridcolor:C.grid,showline:true,linewidth:1,linecolor:C.text};
const LAYOUT_BASE={plot_bgcolor:'white',paper_bgcolor:C.background,
  font:{family:'sans-serif',size:12,color:C.text},hovermode:'x unified',showlegend:true,
  legend:{orientation:'h',yanchor:'bottom',y:1.02,xanchor:'right',x:1},margin:{l:72,r:64,t:56,b:56}};

const ratioTrace={type:'scatter',mode:'lines+markers',x:DATA.dates,y:DATA.values,
  name:'平均维持担保比例(%)',yaxis:'y',line:{color:C.primary,width:2.2},
  marker:{size:4,color:C.primary,line:{width:0}},
  hovertemplate:'<b>日期:</b> %{x}<br><b>维持担保比例:</b> %{y:.2f}%<extra></extra>'};
const indexTrace={type:'scatter',mode:'lines',x:DATA.dates,y:DATA.index,yaxis:'y2',
  name:'上证指数(点)',line:{color:C.navy,width:1.9},
  hovertemplate:'<b>日期:</b> %{x}<br><b>上证指数:</b> %{y:.2f}<extra></extra>'};
const trendTrace={type:'scatter',mode:'lines',x:DATA.dates,y:DATA.trend,yaxis:'y',
  name:'比例线性趋势',line:{color:C.accent,width:1.8,dash:'dash'},
  hovertemplate:'<b>趋势值:</b> %{y:.2f}%<extra></extra>'};
const exTrace={type:'scatter',mode:'markers+text',
  x:[DATA.stats.max_date,DATA.stats.min_date],y:[DATA.stats.max,DATA.stats.min],yaxis:'y',
  name:'比例区间极值',text:['比例高点 '+DATA.stats.max.toFixed(2)+'%','比例低点 '+DATA.stats.min.toFixed(2)+'%'],
  textposition:['top center','bottom center'],textfont:{size:11,color:C.text},
  marker:{size:9,color:'#fff',line:{color:C.primary,width:2.5}},
  hovertemplate:'<b>%{text}</b><br>日期: %{x}<extra></extra>'};
const mainLayout=Object.assign({},LAYOUT_BASE,{
  title:{text:'平均维持担保比例 与 上证指数',x:0.5,font:{size:19,color:C.text,family:'serif'}},
  xaxis:Object.assign({title:'日期',type:'date'},AX),
  yaxis:Object.assign({title:'平均维持担保比例 (%)',side:'left',color:C.primary,tickfont:{color:C.primary}},AX),
  yaxis2:{title:'上证指数 (点)',overlaying:'y',side:'right',showgrid:false,showline:true,linewidth:1,
    linecolor:C.navy,ticks:'outside',tickfont:{color:C.navy},titlefont:{color:C.navy,size:12}},
  height:540,margin:{l:74,r:78,t:72,b:56}});
mainLayout.shapes=[{type:'line',xref:'paper',x0:0,x1:1,y0:DATA.stats.mean,y1:DATA.stats.mean,
  layer:'below',line:{color:C.accent,width:1.5,dash:'dash'}}];
mainLayout.annotations=[{xref:'paper',x:0.004,y:DATA.stats.mean,
  text:'比例均值 '+DATA.stats.mean.toFixed(2)+'%',showarrow:false,xanchor:'left',yanchor:'bottom',yshift:5,
  font:{size:11,color:C.accent}}];
Plotly.newPlot('chart_main',[ratioTrace,indexTrace,trendTrace,exTrace],mainLayout,
  {responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','autoScale2d']});

Plotly.newPlot('chart_norm',[
  {type:'scatter',mode:'lines',x:DATA.dates,y:DATA.norm_ratio,name:'维持担保比例(归一化)',
   line:{color:C.primary,width:2.2},marker:{size:3,color:C.primary},
   hovertemplate:'<b>日期:</b> %{x}<br><b>比例(基期=100):</b> %{y:.2f}<extra></extra>'},
  {type:'scatter',mode:'lines',x:DATA.dates,y:DATA.norm_index,name:'上证指数(归一化)',
   line:{color:C.navy,width:2},
   hovertemplate:'<b>日期:</b> %{x}<br><b>上证(基期=100):</b> %{y:.2f}<extra></extra>'}],
  Object.assign({},LAYOUT_BASE,{
    title:{text:'归一化对比：'+DATA.stats.start+' ＝ 100',x:0.5,font:{size:19,color:C.text,family:'serif'}},
    xaxis:Object.assign({title:'日期',type:'date'},AX),
    yaxis:Object.assign({title:'相对基期涨跌幅 (基期=100)'},AX),
    height:470,margin:{l:74,r:64,t:66,b:56}}),
  {responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','autoScale2d']});

Plotly.newPlot('chart_dd',[{type:'scatter',mode:'lines',x:DATA.dates,y:DATA.drawdown,
  name:'距前高回撤',line:{color:C.primary,width:1.8},fill:'tozeroy',fillcolor:'rgba(237,48,48,0.10)',
  hovertemplate:'<b>日期:</b> %{x}<br><b>距前高回撤:</b> %{y:.2f}%<extra></extra>'}],
  Object.assign({},LAYOUT_BASE,{
    xaxis:Object.assign({title:'日期',type:'date'},AX),
    yaxis:Object.assign({title:'回撤 (%)',rangemode:'tozero'},AX),
    height:420,showlegend:false,margin:{l:72,r:40,t:28,b:56}}),
  {responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','autoScale2d']});

const mLbl=DATA.months.map(m=>m.m);
Plotly.newPlot('chart_month',[
  {type:'scatter',mode:'lines',x:mLbl,y:DATA.months.map(m=>m.lo),
   line:{color:'rgba(96,165,250,0.95)',width:1},showlegend:false,name:'月内最低',
   hovertemplate:'<b>月份:</b> %{x}<br><b>月内最低:</b> %{y:.2f}%<extra></extra>'},
  {type:'scatter',mode:'lines',x:mLbl,y:DATA.months.map(m=>m.hi),
   line:{color:'rgba(96,165,250,0.95)',width:1},fillcolor:'rgba(96,165,250,0.22)',fill:'tonexty',
   showlegend:false,name:'月内最高',
   hovertemplate:'<b>月份:</b> %{x}<br><b>月内最高:</b> %{y:.2f}%<extra></extra>'},
  {type:'scatter',mode:'lines+markers',x:mLbl,y:DATA.months.map(m=>m.v),
   name:'月均值',line:{color:C.primary,width:2.6},marker:{size:4,color:C.primary},
   hovertemplate:'<b>月份:</b> %{x}<br><b>月均值:</b> %{y:.2f}%<extra></extra>'}],
  Object.assign({},LAYOUT_BASE,{
    xaxis:Object.assign({title:'月份',type:'category',tickangle:-45,
      tickmode:'array',tickvals:mLbl.filter((_,i)=>i%3===0),ticktext:mLbl.filter((_,i)=>i%3===0)},AX),
    yaxis:Object.assign({title:'平均维持担保比例 (%)'},AX),
    height:420,margin:{l:72,r:40,t:34,b:78}}),
  {responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','autoScale2d']});

const peak=Math.max.apply(null,DATA.values);
const tbody=document.getElementById('tbody'),cnt=document.getElementById('cnt');
function renderRows(filter){
  const q=(filter||'').trim();let html='',shown=0;
  for(let i=0;i<DATA.dates.length;i++){
    const d=DATA.dates[i];
    if(q&&d.indexOf(q.replace(/-/g,''))<0&&d.indexOf(q)<0) continue;
    shown++;
    const v=DATA.values[i],s=DATA.index[i],ch=DATA.index_chg[i];
    const prev=i>0?DATA.values[i-1]:null;
    const dp=prev===null?null:v-prev;
    const dcls=dp===null?'':(dp>0?'up':(dp<0?'down':''));
    const ds=dp===null?'—':(dp>0?'+':'')+dp.toFixed(2);
    const scls=ch===0?'':(ch>0?'up':'down');
    html+='<tr><td class="num">'+(i+1)+'</td><td>'+d+'</td>'
      +'<td class="num"><b style="color:#ed3030">'+v.toFixed(2)+'</b></td>'
      +'<td class="num" style="color:#1e3a8a"><b>'+s.toFixed(2)+'</b></td>'
      +'<td class="num '+scls+'">'+(ch>0?'+':'')+ch.toFixed(2)+'</td>'
      +'<td class="num '+dcls+'">'+ds+'</td>'
      +'<td class="num">-'+(peak-v).toFixed(2)+'</td></tr>';
  }
  tbody.innerHTML=html;
  cnt.textContent='显示 '+shown+' / '+DATA.dates.length+' 条';
}
renderRows('');
document.getElementById('q').addEventListener('input',e=>renderRows(e.target.value));
</script>
</body></html>`;
}
