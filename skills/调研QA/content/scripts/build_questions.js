#!/usr/bin/env node
/**
 * 调研QA - 需求调研问题生成脚本
 *
 * 用法: node build_questions.js <output_path>
 *
 * 生成包含封面 + 问题总表 + 三个分类子表的 Excel 文件。
 * 依赖: exceljs npm 包（需在 /tmp/xlsx_work 下 npm install）
 */

'use strict';
const ExcelJS = require('exceljs');

const C = {
  NAVY:'1B3A5C', LTBLUE:'D4E4F0', COVER:'E8EEF2',
  BODY:'1A1A1A', ALT:'F4F8FB', WHITE:'FEFEFE',
  CAT: { '历史数据':'2C6E49', '数据对接':'1B3A5C', '需求明确':'7B3F00' },
  CATBG: { '历史数据':'D4EDD4', '数据对接':'D4E4F0', '需求明确':'F5E6D4' },
  PRI: { P0:'E53935', P1:'FB8C00', P2:'5B8DB8' },
};

const ALL_Q = [
  // ── 历史数据 ──────────────────────────────────────────
  ["Q1","历史数据","各系统（Xstore/PIM/BI）商品数据的完整度和准确度如何？是否有已知的缺失或错误数据？","P0"],
  ["Q2","历史数据","历史商品主数据是否有版本管理？数据变更是否有记录可追溯？","P0"],
  ["Q3","历史数据","现有商品数据中图片缺失比例大概是多少？（需量化，作为数据质量基线）","P0"],
  ["Q4","历史数据","PIM中有多少比例的商品同时有中英文详情？有多少只有中文或只有英文？","P0"],
  ["Q5","历史数据","系统是否保留商品价格历史变更记录？目前能追溯多长时间的价格变动？","P0"],
  ["Q6","历史数据","过往 Markdown 促销的历史记录是否需要保留？保留多久？","P1"],
  ["Q7","历史数据","库存数据是否需要保留历史记录（如近30天/90天趋势）？还是只保留最新快照？","P1"],
  ["Q8","历史数据","台湾 TTR POS 的历史库存数据，是否需要接入作为分析依据？","P2"],
  ["Q9","历史数据","目前企微机器人的使用数据（问答记录）是否有积累？量级如何？","P0"],
  ["Q10","历史数据","现有门店导购是否有记录顾客分享、收藏等行为数据？","P1"],
  ["Q11","历史数据","目前企微知识库中有哪些文档？（培训文档/政策/PDF产品手册等）总量多少？","P0"],
  ["Q12","历史数据","现有文档是否已经过结构化处理，还是原始文件堆砌？","P1"],
  ["Q13","历史数据","门店现有搭配图片存量多少？存储在哪里？格式是否统一？","P1"],
  ["Q14","历史数据","过往的搭配图是否有版权或肖像权的授权问题需要清理？","P0"],
  ["Q15","历史数据","是否有现有数据字典或字段映射关系文档？不同系统数据冲突时的决策规则是什么？","P0"],
  ["Q16","历史数据","产品/运营团队现有依赖哪些数据报表？数据来源是哪些系统？","P1"],
  ["Q17","历史数据","是否有已知的「数据孤岛」问题需要在本系统中解决？","P1"],
  ["Q18","历史数据","历史是否有做以图搜图的经验？现有图片是否有打标/标注数据可用于训练？","P2"],
  // ── 数据对接 ──────────────────────────────────────────
  ["Q19","数据对接","Xstore 的 API 接口文档是否已提供？每日同步的时间窗口是固定几点？","P0"],
  ["Q20","数据对接","商品主数据中哪些字段可能出现多系统来源冲突？优先级规则是什么？","P0"],
  ["Q21","数据对接","Xstore 的商品分类有多少级？SAP 分类与业务分类的映射规则谁来做？","P0"],
  ["Q22","数据对接","PIM 的图片更新频率是每日增量还是全量？API 调用频率限制是多少？","P0"],
  ["Q23","数据对接","PIM 中是否存在占位图/无效图片？是否已有标记机制？图片是否有水印？","P0"],
  ["Q24","数据对接","Reva 图片是通过爬虫还是固定 URL 规则获取？URL 规则是什么？","P1"],
  ["Q25","数据对接","Reva 图片更新是否支持增量触发？图片是否可能与 PIM 图片重复？如何去重？","P1"],
  ["Q26","数据对接","Baozun 的尺寸图数据字段格式是什么？是否需要宝尊侧开发接口？","P0"],
  ["Q27","数据对接","Baozun 回传字段是否已确认？字段级映射规则谁来定义？","P0"],
  ["Q28","数据对接","BI 导出库存的字段有哪些？文件格式是 CSV 还是 Excel？每日导出时间是否固定？","P0"],
  ["Q29","数据对接","港澳库存和大陆库存是否来自不同的 BI 实体？字段是否一致？","P1"],
  ["Q30","数据对接","TTR POS 的库存接口文档由谁提供？接口稳定性和响应时间要求是什么？","P0"],
  ["Q31","数据对接","WISE 转发库存的机制是轮询还是推送？增量更新的频率是？故障补录机制是什么？","P0"],
  ["Q32","数据对接","企微网盘的文件同步目录结构是否已确定？同步规则是什么（增量/全量）？","P1"],
  ["Q33","数据对接","同步的文件类型是否有限制？知识库同步后是否需要重新索引？","P1"],
  ["Q34","数据对接","各系统数据同步失败时的告警机制是什么？告警通知给谁？重试策略是什么？","P0"],
  ["Q35","数据对接","各系统 API 的调用权限由谁管理？是否有轮换机制？","P1"],
  ["Q36","数据对接","门店或导购是否有权限直接调用任何后端 API？还是都需要通过后台授权？","P1"],
  ["Q37","数据对接","图片数据（OSS地址）是否需要做防盗链处理？","P1"],
  ["Q38","数据对接","百炼知识库的接入方式是 API 还是向量库直连？调用频率限制是多少？","P0"],
  ["Q39","数据对接","商品知识库与文档知识库是否共享向量模型？还是分开建设？","P0"],
  ["Q40","数据对接","百炼平台的 Token 计费预算上限是多少？谁来监控？","P1"],
  ["Q41","数据对接","前端是否有接口文档规范要求（如响应格式、错误码）？是否需要支持分页？","P1"],
  ["Q42","数据对接","图片 CDN 的域名是否已确定？是否需要配置白名单？","P2"],
  ["Q43","数据对接","微信小程序是否涉及支付功能？还是纯展示功能？","P2"],
  ["Q44","数据对接","商品分享到微信的卡片样式是否有定制要求（如缩略图、标题格式）？","P2"],
  ["Q45","数据对接","除了百炼，是否有计划接入其他 LLM（如 GPT/Claude）作为备选？","P2"],
  ["Q46","数据对接","AI 回答中涉及商品价格等信息时，是否需要人工审核后发布？","P1"],
  ["Q47","数据对接","系统数据库是否需要做异地备份？备份频率是多少？关键系统故障时降级方案是什么？","P0"],
  ["Q48","数据对接","商品数据、库存数据是否涉及 GDPR（港澳）或其他数据合规要求？","P0"],
  ["Q49","数据对接","用户行为日志（问答记录、分享记录）的保留周期是多久？是否有数据脱敏要求？","P0"],
  // ── 需求明确 ──────────────────────────────────────────
  ["Q50","需求明确","后台用户角色有哪些？（管理员/运营/店长）各角色的权限边界是什么？","P0"],
  ["Q51","需求明确","后台是否需要支持多语言（如繁体中文）？日活跃用户数峰值预估是多少？","P1"],
  ["Q52","需求明确","商品筛选条件中，Family、Markdown 等属性是否需要作为必选筛选项？","P0"],
  ["Q53","需求明确","商品列表是否需要支持批量操作（如批量打标签、批量上架）？","P1"],
  ["Q54","需求明确","分类映射中，一对多映射的映射关系由谁维护（业务方还是 IT）？","P0"],
  ["Q55","需求明确","商品详情页中，哪些字段是只读的（来自接口）、哪些字段可编辑（用户上传）？","P0"],
  ["Q56","需求明确","商品的多语言描述（英文/繁体）是否需要在详情页展示？展示优先级是什么？","P1"],
  ["Q57","需求明确","商品的尺码表（尺寸图）展示格式是否有特殊要求（如欧码/美码切换）？","P1"],
  ["Q58","需求明确","图片上传的审核流程是怎样？需要几级审批？后台与门店的审核流程是否区别处理？","P0"],
  ["Q59","需求明确","图片水印规则是什么？谁来承担水印生成的工作？","P1"],
  ["Q60","需求明确","搭配图片是否允许门店员工上传？还是仅限后台管理人员上传？","P0"],
  ["Q61","需求明确","搭配图中的商品关联关系，支持批量导入吗？导入文件格式是什么？","P1"],
  ["Q62","需求明确","搭配图如果涉及真人模特，肖像授权文件是否需要上传存档？","P0"],
  ["Q63","需求明确","标签的创建权限是否需要限制（如仅管理员可创建）？","P1"],
  ["Q64","需求明确","自动打标规则（如按系列属性自动打标签）的触发逻辑由谁配置？","P1"],
  ["Q65","需求明确","标签是否支持有效期（如季节性标签自动过期）？","P2"],
  ["Q66","需求明确","首页的分类、标签、Banner 配置能力，是否在第一阶段就交付？","P1"],
  ["Q67","需求明确","前端首页是否需要 A/B 测试能力？门店营销活动时首页配置权限是否可以下放给店长？","P1"],
  ["Q68","需求明确","AI 问答是否需要支持多轮对话（上下文记忆）？记忆轮数上限多少？","P0"],
  ["Q69","需求明确","AI 无法回答的问题，是否需要记录并触发知识库更新流程？","P0"],
  ["Q70","需求明确","用户对 AI 回答的满意度评分（点赞/点踩）是否需要展示在机器人界面？","P1"],
  ["Q71","需求明确","多个知识库（商品库/SOP库/IT培训库）之间的隔离规则是什么？","P0"],
  ["Q72","需求明确","知识库内容更新后，是否需要重新训练模型？还是实时生效？","P0"],
  ["Q73","需求明确","知识库的访问权限是否需要按门店/部门隔离？","P0"],
  ["Q74","需求明确","导购切换门店的逻辑是什么？一次只能属于一家门店还是可以多店？","P0"],
  ["Q75","需求明确","拍照识图的准确率预期是多少？是否有最低验收标准（如 Top3 包含正确答案）？","P0"],
  ["Q76","需求明确","商品分享清单是否需要支持草稿状态（创建后暂不发送）？","P1"],
  ["Q77","需求明确","C 端用户是否需要注册/登录？还是通过导购分享直接访问？","P0"],
  ["Q78","需求明确","用户收藏的清单，是否需要支持按时间/按导购筛选？","P1"],
  ["Q79","需求明确","一个导购离职后，其分享的清单顾客是否仍可访问？","P0"],
  ["Q80","需求明确","大陆/港澳/台湾三地的价格展示字段是否一致？货币单位如何处理？","P0"],
  ["Q81","需求明确","价格变动曲线图，需要展示多长时间的历史（1个月/3个月/1年）？","P1"],
  ["Q82","需求明确","促销价格（Markdown Price）与原价（MSRP）的展示优先级是什么？","P0"],
  ["Q83","需求明确","门店无库存的商品，是否允许导购分享给顾客？顾客端如何展示？","P0"],
  ["Q84","需求明确","库存数据 T+1 的时效性是否已和业务方确认？顾客是否有预期管理需求？","P0"],
  ["Q85","需求明确","其他门店库存的展示，是否需要显示具体店铺名称还是只显示区域汇总？","P1"],
  ["Q86","需求明确","分享清单是否有有效期？过期后顾客是否还能查看？一个清单是否可以被多次分享？","P1"],
  ["Q87","需求明确","分享清单的浏览数据（PV/UV）是否需要实时更新？还是定时刷新？","P2"],
  ["Q88","需求明确","企微机器人的消息格式是否只能纯文本+图片？是否需要支持卡片消息？","P0"],
  ["Q89","需求明确","机器人回答商品信息时，是否需要在文字中插入小程序链接？","P1"],
  ["Q90","需求明确","不同地区（大陆/港澳/台湾）的企微机器人是否共用同一个知识库入口？","P0"],
  ["Q91","需求明确","H5 嵌入 WhatsApp/Line 后，功能范围是否与企微机器人一致？","P0"],
  ["Q92","需求明确","H5 页面是否需要支持离线缓存？港澳台地区 H5 的服务器部署在哪里？","P1"],
  ["Q93","需求明确","香港、澳门、台湾的权限控制粒度是否只到门店级别？","P0"],
  ["Q94","需求明确","组织架构（门店/区域/部门）的数据来源是哪里？（企微组织还是独立配置）","P1"],
  ["Q95","需求明确","员工离职或调岗后，权限回收的时效要求是多少（24h/48h/即时）？","P0"],
  ["Q96","需求明确","AI 问答的数据看板需要展示哪些指标？（日问答量/成功率/Top未回答问题）","P1"],
  ["Q97","需求明确","商品查询的数据看板需要哪些维度？（搜索关键词/商品点击量/分享转化率）","P1"],
  ["Q98","需求明确","数据报表是否需要支持导出？导出格式是什么？","P2"],
  ["Q99","需求明确","第一阶段上线前，是否需要有数据验收（Data UAT）环节？","P0"],
  ["Q100","需求明确","第一阶段和第二阶段之间，是否预留缓冲时间用于问题修复？","P1"],
  ["Q101","需求明确","上线后是否有分批门店试点计划？还是全量一次性上线？","P0"],
  ["Q102","需求明确","系统支持的并发用户数预估是多少？响应时间要求是否明确？","P0"],
  ["Q103","需求明确","核心接口（P0 级）的 SLA 要求是多少？图片加载是否有 CDN 加速？","P0"],
  ["Q104","需求明确","百炼/阿里云服务如果出现故障，系统是否有降级方案？","P0"],
  ["Q105","需求明确","各外部系统 API 版本是否有锁定？Sandbox 测试环境是否已申请到位？","P1"],
  ["Q106","需求明确","运营知识库的内容录入和审核流程是什么？谁负责内容的准确性？","P0"],
  ["Q107","需求明确","知识库内容的更新频率是多少？是否有内容过期机制（如过季促销信息自动下架）？","P1"],
  ["Q108","需求明确","知识库与商品库的内容交叉引用如何维护（如商品保养说明关联商品详情）？","P1"],
  ["Q109","需求明确","门店导购遇到系统问题的反馈渠道是什么？故障应急响应机制是什么？","P1"],
  ["Q110","需求明确","重大故障（超过 X 分钟）的通知升级流程是什么？","P1"],
  ["Q111","需求明确","竞品（如 LVMH）的商品信息管理有哪些值得借鉴的功能？","P2"],
  ["Q112","需求明确","行业通用标准（如 GS1 商品条码规范）是否需要在系统中落地？","P2"],
  ["Q113","需求明确","项目交付物清单是否已明确？验收标准（SLA/UAT 通过率）是什么？","P0"],
  ["Q114","需求明确","交付后是否需要提供运维手册和培训文档？","P1"],
  ["Q115","需求明确","第二阶段的功能范围是否有初步排期？还是等第一阶段验收后再规划？","P1"],
  ["Q116","需求明确","文档中 Q1（英文详情获取）的问题目前是否已有结论？","P0"],
  ["Q117","需求明确","PIM 中图片占位图的识别标准是否已和 PIM 团队对齐？","P0"],
  ["Q118","需求明确","搭配图肖像权问题（员工离职后图片处理）是否有明确的合规处理方案？","P0"],
];

// ── Color helpers ──────────────────────────────────────────────────────────────
function fmtHex(hex) {
  if (!hex) return 'FFFFFF';
  const clean = hex.startsWith('#') ? hex.slice(1) : hex;
  return clean.length === 8 ? clean.slice(2) : clean;
}

function mkFill(hex) {
  return { type:'pattern', pattern:'solid', fgColor:{ argb:'FF'+fmtHex(hex) } };
}
function mkFont(bold, size, color, italic) {
  return { bold, size, color:{ argb:'FF'+fmtHex(color) }, italic:!!italic };
}
function mkBorder() {
  const s = { style:'thin', color:{ argb:'FFCBCBCB' } };
  return { top:s, bottom:s, left:s, right:s };
}
function center(wrap) { return { horizontal:'center', vertical:'middle', wrapText:!!wrap }; }
function left(wrap) { return { horizontal:'left', vertical:'middle', wrapText:!!wrap }; }

// ── Cover sheet ────────────────────────────────────────────────────────────────
function buildCover(wb, qcount) {
  const ws = wb.addWorksheet('封面');
  ws.state = 'visible';
  ws.views = [{ showGridLines:false }];
  ws.columns = [
    {width:3},{width:20},{width:46},{width:16},{width:14},{width:14},{width:3}
  ];

  ws.getRow(4).height = 52;
  ws.mergeCells('B4:F4');
  const t = ws.getCell('B4');
  t.value = '需求调研问题清单';
  t.font = mkFont(true, 20, C.NAVY);
  t.fill = mkFill(C.COVER);
  t.alignment = center();

  ws.getRow(5).height = 28;
  ws.mergeCells('B5:F5');
  const s = ws.getCell('B5');
  s.value = '基于材料自动生成  |  需求调研阶段专用';
  s.font = mkFont(false, 12, '5B8DB8');
  s.fill = mkFill(C.COVER);
  s.alignment = center();

  ws.getRow(6).height = 5;
  for(let c=2;c<=6;c++) ws.getCell(6,c).fill = mkFill(C.NAVY);

  const info = [
    [8,'项目名称','（待填写）'],
    [9,'当前阶段','需求调研'],
    [10,'文档版本','v1.0'],
    [11,'编制日期', new Date().toISOString().slice(0,10)],
    [12,'制表人','产品经理'],
    [13,'问题总数', String(qcount)+' 问'],
    [14,'维度分类','历史数据 / 数据对接 / 需求明确'],
  ];
  info.forEach(([row,lbl,val]) => {
    ws.getRow(row).height = 26;
    const lc = ws.getCell(row,2);
    lc.value = lbl; lc.font = mkFont(true,11,'5B8DB8');
    lc.fill = mkFill('F2F6FA'); lc.alignment = left(); lc.border = mkBorder();
    ws.mergeCells(row,3,row,6);
    const vc = ws.getCell(row,3);
    vc.value = val; vc.font = mkFont(false,11,C.BODY);
    vc.fill = mkFill(C.WHITE); vc.alignment = left(); vc.border = mkBorder();
  });

  ws.getRow(17).height = 28;
  const ih = ws.getCell(17,2);
  ih.value = '工作表目录'; ih.font = mkFont(true,12,C.NAVY);
  ih.fill = mkFill(C.COVER); ih.alignment = left();

  const catCount = (cat) => ALL_Q.filter(q=>q[1]===cat).length;
  const dir = [
    ['封面','本文档封面与导航'],
    ['问题总表','完整问题列表，按维度分类，彩色优先级标签'],
    ['历史数据',`历史数据相关问题（Q1–Q${catCount('历史数据')}，共${catCount('历史数据')}问）`],
    ['数据对接',`数据对接相关问题（Q${catCount('历史数据')+1}–Q${catCount('历史数据')+catCount('数据对接')}，共${catCount('数据对接')}问）`],
    ['需求明确',`需求明确相关问题（Q${catCount('历史数据')+catCount('数据对接')+1}–Q${qcount}，共${catCount('需求明确')}问）`],
  ];
  dir.forEach(([sn,sd],i)=>{
    const row = 18+i;
    ws.getRow(row).height = 22;
    const sc = ws.getCell(row,2);
    sc.value = sn; sc.font = mkFont(true,10,C.NAVY);
    sc.fill = mkFill('F2F6FA'); sc.alignment = left(); sc.border = mkBorder();
    ws.mergeCells(row,3,row,6);
    const dc = ws.getCell(row,3);
    dc.value = sd; dc.font = mkFont(false,10,C.BODY);
    dc.fill = mkFill(C.WHITE); dc.alignment = left(); dc.border = mkBorder();
  });

  ws.mergeCells('B26:F26');
  const disc = ws.getCell(26,2);
  disc.value = '⚠  本文档仅供内部需求调研使用，内容随调研推进持续更新。';
  disc.font = mkFont(false,9,'888888',true); disc.alignment = left();
}

// ── Summary sheet ──────────────────────────────────────────────────────────────
function buildSummary(wb) {
  const ws = wb.addWorksheet('问题总表');
  ws.views = [{ showGridLines:false }];
  ws.columns = [
    {width:7},{width:12},{width:48},{width:10},{width:12},{width:22}
  ];

  ws.getRow(2).height = 42;
  ws.mergeCells('A2:F2');
  const ct = ws.getCell('A2');
  ct.value = '需求调研问题总表（'+ALL_Q.length+'问）';
  ct.font = mkFont(true,15,C.WHITE);
  ct.fill = mkFill(C.NAVY); ct.alignment = center();

  ws.getRow(3).height = 24;
  ['序号','维度','问题内容','优先级','状态','备注/负责人'].forEach((h,i)=>{
    const c = ws.getCell(3,i+1);
    c.value = h; c.font = mkFont(true,11,C.WHITE);
    c.fill = mkFill(C.NAVY); c.alignment = center(true); c.border = mkBorder();
  });

  ALL_Q.forEach((q,r)=>{
    const [no,cat,text,prio] = q;
    const row = r+4;
    const bg = row%2===0 ? C.ALT : C.WHITE;
    ws.getRow(row).height = 38;

    const c1 = ws.getCell(row,1);
    c1.value = no; c1.font = mkFont(true,10,C.BODY);
    c1.fill = mkFill(bg); c1.alignment = center(); c1.border = mkBorder();

    const c2 = ws.getCell(row,2);
    c2.value = cat;
    c2.font = mkFont(true,10,C.CAT[cat]);
    c2.fill = mkFill(C.CATBG[cat]);
    c2.alignment = center(true); c2.border = mkBorder();

    const c3 = ws.getCell(row,3);
    c3.value = text;
    c3.font = mkFont(false,10,C.BODY);
    c3.fill = mkFill(bg); c3.alignment = left(true); c3.border = mkBorder();

    const c4 = ws.getCell(row,4);
    c4.value = prio;
    c4.font = mkFont(true,10,C.WHITE);
    c4.fill = mkFill(C.PRI[prio]);
    c4.alignment = center(); c4.border = mkBorder();

    const c5 = ws.getCell(row,5);
    c5.value = '待确认'; c5.font = mkFont(false,10,C.BODY);
    c5.fill = mkFill(bg); c5.alignment = center(); c5.border = mkBorder();

    const c6 = ws.getCell(row,6);
    c6.value = ''; c6.font = mkFont(false,10,'888888');
    c6.fill = mkFill(bg); c6.alignment = left(); c6.border = mkBorder();
  });
}

// ── Category sheet ────────────────────────────────────────────────────────────
function buildCatSheet(wb, name, cat, hdrColor) {
  const ws = wb.addWorksheet(name);
  ws.views = [{ showGridLines:false }];
  ws.columns = [
    {width:7},{width:54},{width:10},{width:12},{width:24}
  ];

  ws.getRow(2).height = 42;
  ws.mergeCells('A2:E2');
  const ct = ws.getCell('A2');
  ct.value = `${name}  —  需求调研问题清单`;
  ct.font = mkFont(true,16,C.WHITE);
  ct.fill = mkFill(hdrColor); ct.alignment = center();

  ws.getRow(3).height = 26;
  ['序号','问题内容','优先级','状态','备注/负责人'].forEach((h,i)=>{
    const c = ws.getCell(3,i+1);
    c.value = h; c.font = mkFont(true,11,C.WHITE);
    c.fill = mkFill(hdrColor); c.alignment = center(true); c.border = mkBorder();
  });

  const filtered = ALL_Q.filter(q=>q[1]===cat);
  filtered.forEach((q,r)=>{
    const [no,,text,prio] = q;
    const row = r+4;
    const bg = row%2===0 ? C.ALT : C.WHITE;
    ws.getRow(row).height = 38;

    const c1 = ws.getCell(row,1);
    c1.value = no; c1.font = mkFont(true,10,hdrColor);
    c1.fill = mkFill(bg); c1.alignment = center(); c1.border = mkBorder();

    const c2 = ws.getCell(row,2);
    c2.value = text; c2.font = mkFont(false,10,C.BODY);
    c2.fill = mkFill(bg); c2.alignment = left(true); c2.border = mkBorder();

    const c3 = ws.getCell(row,3);
    c3.value = prio; c3.font = mkFont(true,10,C.WHITE);
    c3.fill = mkFill(C.PRI[prio]);
    c3.alignment = center(); c3.border = mkBorder();

    const c4 = ws.getCell(row,4);
    c4.value = '待确认'; c4.font = mkFont(false,10,C.BODY);
    c4.fill = mkFill(bg); c4.alignment = center(); c4.border = mkBorder();

    const c5 = ws.getCell(row,5);
    c5.value = ''; c5.font = mkFont(false,10,'888888');
    c5.fill = mkFill(bg); c5.alignment = left(); c5.border = mkBorder();
  });
}

// ── Main ───────────────────────────────────────────────────────────────────────
const outPath = process.argv[2] || '/workspace/需求调研问题清单.xlsx';
const wb = new ExcelJS.Workbook();

buildCover(wb, ALL_Q.length);
buildSummary(wb);
buildCatSheet(wb,'历史数据','历史数据','2C6E49');
buildCatSheet(wb,'数据对接','数据对接','1B3A5C');
buildCatSheet(wb,'需求明确','需求明确','7B3F00');

wb.xlsx.writeFile(outPath)
  .then(()=>{ console.log('✅ Saved:', outPath, `| 共 ${ALL_Q.length} 问`); })
  .catch(e=>{ console.error('❌', e.message); process.exit(1); });