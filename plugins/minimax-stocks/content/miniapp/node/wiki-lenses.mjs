// @ts-check
// 内置分析视角（LLM-Wiki know-how）。用户可以在页面上改写、停用、恢复默认或新建自己的视角。

export const DEFAULT_PURPOSE = '';

export const BUILTIN_LENSES = Object.freeze([
  {
    id: 'chain',
    name: '产业链视角',
    enabled: true,
    prompt: [
      '从产业链视角拆解资料：',
      '- 识别资料所属行业，把行业拆成上游（原材料、零部件、设备、基础软件/IP）、中游（制造、集成、核心产品）、下游（应用场景、终端客户）的具体环节，每个环节建一个 segment 页并标注 chain。',
      '- 环节页写清：做什么、关键产品与技术路线、价值量或成本占比（资料有才写）、技术壁垒、国产化率与集中度、代表公司。',
      '- 公司页写清：所处环节、主营产品与收入结构、核心客户与供应商、在环节中的地位；能确定股票代码时填入 tickers（A 股用 600519.SH / 300308.SZ 格式）。',
      '- 用关系表达链条：环节之间用 upstream_of（上游 → 下游），公司到环节用 belongs_to，公司之间的供货用 supplies（供应方 → 采购方），公司到产品用 produces。',
      '- 重点标出卡脖子环节、价值量最高的环节、利润最集中的环节，以及资料提到的瓶颈和扩产节奏。',
    ].join('\n'),
  },
  {
    id: 'supply-demand',
    name: '供需视角',
    enabled: true,
    prompt: [
      '从供需视角整理资料：',
      '- 需求侧：下游需求的驱动因素、需求规模与增速（写明口径、年份和出处）、季节性和所处周期位置。',
      '- 供给侧：主要产能与扩产计划、产能利用率、良率与爬坡周期、新进入者、进出口与地缘约束。',
      '- 价格与库存：价格趋势、库存周期阶段、价格弹性；判断当前是紧平衡、过剩还是短缺，并写明依据。',
      '- 把供需判断写进对应行业页或环节页的「供需」小节；影响供需的政策或事件建 event 页，用 drives 关系连到受影响的环节或公司。',
      '- 预测数字标注「预测」并写明机构与发布时间，不和实际值混写。',
    ].join('\n'),
  },
  {
    id: 'competition',
    name: '竞争格局视角',
    enabled: true,
    prompt: [
      '从竞争视角整理资料：',
      '- 每个关键环节列出主要参与者和市场份额（写明口径和年份），判断集中度（CR3 / CR5）和格局类型（垄断、寡头、分散）。',
      '- 拆解竞争要素：技术路线、成本、客户认证、规模、渠道；说明护城河和替代威胁。',
      '- 公司之间用 competes 关系连接，替代技术或替代产品用 substitutes 连接。',
      '- 记录国产替代进展、份额变化趋势，以及价格战、扩产竞赛等信号。',
      '- 不同来源观点不一致时，在页面里并列写出各自说法和出处，不要擅自合并成一个结论。',
    ].join('\n'),
  },
  {
    id: 'financials',
    name: '财务与估值视角',
    enabled: false,
    prompt: [
      '提取与产业链环节相关的财务信息：',
      '- 各公司营收、毛利率、净利率、ROE 及趋势，与同环节公司对比，说明利润在产业链中如何分配。',
      '- 资本开支、研发投入、在手订单、合同负债等前瞻指标。',
      '- 资料给出的估值（PE / PS / EV/EBITDA）和目标价必须写明机构与日期，并标为观点，不作为事实。',
    ].join('\n'),
  },
  {
    id: 'policy',
    name: '政策与事件视角',
    enabled: false,
    prompt: [
      '跟踪影响产业链的政策与事件：',
      '- 产业政策、补贴、出口管制、关税、行业标准；重大订单、技术突破、事故、扩产或减产公告。',
      '- 每个事件建 event 页，写清时间、主体、影响方向和受影响的环节或公司，用 drives 关系连接。',
      '- 区分已发生的事实与市场预期，写明日期和出处。',
    ].join('\n'),
  },
]);

export const LENS_LIMITS = Object.freeze({ count: 12, name: 30, prompt: 6000, purpose: 2000 });

function lensError(message) {
  const error = new Error(message);
  /** @type {any} */ (error).code = 'INVALID_LENSES';
  return error;
}

/** 读盘数据与内置视角合并：新版本增加的内置视角会自动出现。 */
export function normalizeLensState(stored) {
  const value = stored && typeof stored === 'object' ? stored : {};
  const saved = Array.isArray(value.lenses) ? value.lenses : [];
  const byId = new Map(saved.filter((lens) => lens && typeof lens.id === 'string').map((lens) => [lens.id, lens]));
  const lenses = [];
  for (const builtin of BUILTIN_LENSES) {
    const own = byId.get(builtin.id);
    lenses.push({
      id: builtin.id,
      name: typeof own?.name === 'string' && own.name.trim() ? own.name.trim().slice(0, LENS_LIMITS.name) : builtin.name,
      prompt: typeof own?.prompt === 'string' && own.prompt.trim() ? own.prompt.slice(0, LENS_LIMITS.prompt) : builtin.prompt,
      enabled: typeof own?.enabled === 'boolean' ? own.enabled : builtin.enabled,
      builtin: true,
      modified: Boolean(own && ((own.prompt && own.prompt !== builtin.prompt) || (own.name && own.name !== builtin.name))),
    });
  }
  for (const lens of saved) {
    if (!lens || typeof lens.id !== 'string' || !lens.id.startsWith('custom-') || lenses.some((item) => item.id === lens.id)) continue;
    if (typeof lens.name !== 'string' || !lens.name.trim() || typeof lens.prompt !== 'string' || !lens.prompt.trim()) continue;
    lenses.push({ id: lens.id.slice(0, 40), name: lens.name.trim().slice(0, LENS_LIMITS.name), prompt: lens.prompt.slice(0, LENS_LIMITS.prompt), enabled: lens.enabled !== false, builtin: false, modified: false });
    if (lenses.length >= LENS_LIMITS.count) break;
  }
  return { purpose: typeof value.purpose === 'string' ? value.purpose.slice(0, LENS_LIMITS.purpose) : DEFAULT_PURPOSE, lenses };
}

/** 校验页面提交的整份视角配置。 */
export function validateLensUpdate(payload) {
  if (!payload || typeof payload !== 'object') throw lensError('视角配置必须是对象');
  if (payload.purpose !== undefined && (typeof payload.purpose !== 'string' || payload.purpose.length > LENS_LIMITS.purpose)) {
    throw lensError('研究目标最多 ' + LENS_LIMITS.purpose + ' 字');
  }
  if (!Array.isArray(payload.lenses)) throw lensError('lenses 必须是数组');
  if (payload.lenses.length > LENS_LIMITS.count) throw lensError('最多 ' + LENS_LIMITS.count + ' 个视角');
  const ids = new Set();
  const lenses = payload.lenses.map((lens, index) => {
    if (!lens || typeof lens !== 'object') throw lensError('第 ' + (index + 1) + ' 个视角格式不对');
    const builtin = BUILTIN_LENSES.find((item) => item.id === lens.id);
    const id = builtin ? builtin.id : typeof lens.id === 'string' && /^custom-[a-z0-9-]{1,32}$/.test(lens.id) ? lens.id : null;
    if (!id) throw lensError('第 ' + (index + 1) + ' 个视角的 id 不合法');
    if (ids.has(id)) throw lensError('视角 id 重复');
    ids.add(id);
    const name = typeof lens.name === 'string' ? lens.name.trim() : '';
    if (!name || name.length > LENS_LIMITS.name) throw lensError('视角名称需要 1–' + LENS_LIMITS.name + ' 个字');
    const prompt = typeof lens.prompt === 'string' ? lens.prompt.replace(/\r\n?/g, '\n').trim() : '';
    if (!prompt || prompt.length > LENS_LIMITS.prompt) throw lensError('「' + name + '」的 Prompt 需要 1–' + LENS_LIMITS.prompt + ' 字');
    return { id, name, prompt, enabled: lens.enabled !== false };
  });
  return { purpose: typeof payload.purpose === 'string' ? payload.purpose.trim() : '', lenses };
}
