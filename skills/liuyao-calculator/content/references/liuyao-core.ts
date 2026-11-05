// 六爻测算核心算法 - 遵循增删卜易野鹤老人古法
// 此文件包含六爻测算的完整算法逻辑

// ==================== 常量定义 ====================

// 天干
export const HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];

// 地支
export const EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

// 五行及对应关系
export const FIVE_ELEMENTS: Record<string, { element: string; yinYang: string }> = {
  '甲': { element: '木', yinYang: '阳' },
  '乙': { element: '木', yinYang: '阴' },
  '丙': { element: '火', yinYang: '阳' },
  '丁': { element: '火', yinYang: '阴' },
  '戊': { element: '土', yinYang: '阳' },
  '己': { element: '土', yinYang: '阴' },
  '庚': { element: '金', yinYang: '阳' },
  '辛': { element: '金', yinYang: '阴' },
  '壬': { element: '水', yinYang: '阳' },
  '癸': { element: '水', yinYang: '阴' },
  '子': { element: '水', yinYang: '阳' },
  '丑': { element: '土', yinYang: '阴' },
  '寅': { element: '木', yinYang: '阳' },
  '卯': { element: '木', yinYang: '阴' },
  '辰': { element: '土', yinYang: '阳' },
  '巳': { element: '火', yinYang: '阴' },
  '午': { element: '火', yinYang: '阳' },
  '未': { element: '土', yinYang: '阴' },
  '申': { element: '金', yinYang: '阳' },
  '酉': { element: '金', yinYang: '阴' },
  '戌': { element: '土', yinYang: '阳' },
  '亥': { element: '水', yinYang: '阴' },
};

// 五行相生
export const ELEMENT_BIRTH: Record<string, string[]> = {
  '木': ['火'], '火': ['土'], '土': ['金'], '金': ['水'], '水': ['木'],
};

// 五行相克
export const ELEMENT_BATTLE: Record<string, string[]> = {
  '木': ['土'], '土': ['水'], '水': ['火'], '火': ['金'], '金': ['木'],
};

// 八卦（从上爻到初爻排列的二进制码）
export const EIGHT_TRIGRAMS: Record<string, { name: string; gua: string; element: string; yin: boolean }> = {
  '111': { name: '乾', gua: '☰', element: '金', yin: false },
  '110': { name: '兑', gua: '☱', element: '金', yin: true },
  '101': { name: '离', gua: '☲', element: '火', yin: true },
  '100': { name: '震', gua: '☳', element: '木', yin: false },
  '011': { name: '巽', gua: '☴', element: '木', yin: true },
  '010': { name: '坎', gua: '☵', element: '水', yin: false },
  '001': { name: '艮', gua: '☶', element: '土', yin: true },
  '000': { name: '坤', gua: '☷', element: '土', yin: false },
};

// 六神
export const SIX_BEASTS = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武'];

// 周易64卦卦辞
export const ZHOU_YI_HEXAGRAM_TEXTS: Record<string, { guaCi: string; tiTan: string }> = {
  '乾': { guaCi: '元亨利贞', tiTan: '天行健，君子以自强不息' },
  '坤': { guaCi: '元亨利牝马之贞，君子有攸往，先迷后得主，利西南得朋，东北丧朋，安贞吉', tiTan: '地势坤，君子以厚德载物' },
  '屯': { guaCi: '元亨利贞，勿用有攸往，利建侯', tiTan: '云雷屯，君子以经纶' },
  '蒙': { guaCi: '亨，匪我求童蒙，童蒙求我，初筮告，再三渎，渎则不告，利贞', tiTan: '山下出泉，蒙；君子以果行育德' },
  '需': { guaCi: '有孚，光亨，贞吉，利涉大川', tiTan: '云上于天，需；君子以饮食宴乐' },
  '讼': { guaCi: '有孚，窒，惕，中吉，终凶，利见大人，不利涉大川', tiTan: '天与水违行，讼；君子以作事谋始' },
  '师': { guaCi: '贞，丈人吉，无咎', tiTan: '地中有水，师；君子以容民畜众' },
  '比': { guaCi: '吉，原筮元永贞，无咎，不宁方来，后夫凶', tiTan: '地上有水，比；先王以建万国，亲诸侯' },
  '泰': { guaCi: '小往大来，吉亨', tiTan: '天地交，泰；后以财成天地之道' },
  '否': { guaCi: '否之匪人，不利君子贞，大往小来', tiTan: '天地不交，否；君子以俭德辟难' },
  '同人': { guaCi: '同人于野，亨，利涉大川，利君子贞', tiTan: '天与火，同人；君子以类族辨物' },
  '大有': { guaCi: '元亨', tiTan: '火在天上，大有；君子以遏恶扬善' },
  '谦': { guaCi: '亨，君子有终', tiTan: '地中有山，谦；君子以裒多益寡' },
  '豫': { guaCi: '利建侯行师', tiTan: '雷出地奋，豫；先王以作乐崇德' },
  '随': { guaCi: '元亨利贞，无咎', tiTan: '泽中有雷，随；君子以向晦入宴息' },
  '蛊': { guaCi: '元亨，利涉大川，先甲三日，后甲三日', tiTan: '山下有风，蛊；君子以振民育德' },
  '临': { guaCi: '元亨利贞，至于八月有凶', tiTan: '泽上有地，临；君子以教思无穷' },
  '观': { guaCi: '盥而不荐，有孚颙若', tiTan: '风行地上，观；先王以省方观民设教' },
  '噬嗑': { guaCi: '亨，利用狱', tiTan: '雷电噬嗑；先王以明罚敕法' },
  '贲': { guaCi: '亨，小利有所往', tiTan: '山下有火，贲；君子以明庶政' },
  '剥': { guaCi: '不利有攸往', tiTan: '山附于地，剥；上以厚下安宅' },
  '复': { guaCi: '亨，出入无疾，朋来无咎，反复其道，七日来复，利有攸往', tiTan: '雷在地中，复；先王以至日闭关' },
  '无妄': { guaCi: '元亨利贞，其匪正有眚，不利有攸往', tiTan: '天下雷行，物与无妄；先王以茂对时' },
  '大畜': { guaCi: '利贞，不家食吉，利涉大川', tiTan: '天在山中，大畜；君子以多识前言往行' },
  '颐': { guaCi: '贞吉，观颐，自求口实', tiTan: '山下有雷，颐；君子以慎言语，节饮食' },
  '大过': { guaCi: '栋桡，利有攸往，亨', tiTan: '泽灭木，大过；君子以独立不惧' },
  '坎': { guaCi: '习坎，有孚，维心亨，行有尚', tiTan: '水洊至，习坎；君子以常德行' },
  '离': { guaCi: '畜牝牛，吉', tiTan: '明两作，离；大人以继明照于四方' },
  '咸': { guaCi: '亨，利贞，取女吉', tiTan: '山上有泽，咸；君子以虚受人' },
  '恒': { guaCi: '亨，无咎，利贞，利有攸往', tiTan: '雷风，恒；君子以立不易方' },
  '遁': { guaCi: '亨，小利贞', tiTan: '天下有山，遁；君子以远小人' },
  '大壮': { guaCi: '利贞', tiTan: '雷在天上，大壮；君子以非礼弗履' },
  '晋': { guaCi: '康侯用锡马蕃庶，昼日三接', tiTan: '明出地上，晋；君子以自昭明德' },
  '明夷': { guaCi: '利艰贞', tiTan: '明入地中，明夷；君子以莅众' },
  '家人': { guaCi: '利女贞', tiTan: '风自火出，家人；君子以言有物' },
  '睽': { guaCi: '小事吉', tiTan: '上火下泽，睽；君子以同而异' },
  '蹇': { guaCi: '利西南，不利东北，利见大人，贞吉', tiTan: '山上有水，蹇；君子以反身修德' },
  '解': { guaCi: '利西南，无所往，其来复吉，有攸往，夙吉', tiTan: '雷雨作，解；君子以赦过宥罪' },
  '损': { guaCi: '有孚，元吉，无咎，可贞，利有攸往', tiTan: '山下有泽，损；君子以惩忿窒欲' },
  '益': { guaCi: '利有攸往，利涉大川', tiTan: '风雷，益；君子以见善则迁' },
  '夬': { guaCi: '扬于王庭，孚号有厉，告自邑，不利即戎，利有攸往', tiTan: '泽上于天，夬；君子以施禄及下' },
  '姤': { guaCi: '女壮，勿用取女', tiTan: '天下有风，姤；后以施命诰四方' },
  '萃': { guaCi: '亨，王假有庙，利见大人，亨利贞，用大牲吉', tiTan: '泽上于地，萃；君子以除戎器' },
  '升': { guaCi: '南征吉，志行也', tiTan: '地中生木，升；君子以顺德' },
  '困': { guaCi: '亨，贞大人吉，无咎，有言不信', tiTan: '泽无水，困；君子以致命遂志' },
  '井': { guaCi: '改邑不改井，无丧无得，往来井井，汔至亦未繘井', tiTan: '木上有水，井；君子以劳民劝相' },
  '革': { guaCi: '巳日乃孚，元亨利贞，悔亡', tiTan: '泽中有火，革；君子以治历明时' },
  '鼎': { guaCi: '元吉，亨', tiTan: '木上有火，鼎；君子以正位凝命' },
  '震': { guaCi: '亨，震来虩虩，笑言哑哑，震惊百里', tiTan: '洊雷，震；君子以恐惧修省' },
  '艮': { guaCi: '艮其背，不获其身，行其庭，不见其人，无咎', tiTan: '兼山，艮；君子以思不出其位' },
  '渐': { guaCi: '女归吉，利贞', tiTan: '山上有木，渐；君子以居贤德善俗' },
  '归妹': { guaCi: '征凶，无攸利', tiTan: '泽上有雷，归妹；君子以永终知敝' },
  '丰': { guaCi: '亨，王假之，勿忧，宜日中', tiTan: '雷电皆至，丰；君子以折狱致刑' },
  '旅': { guaCi: '小亨，旅贞吉', tiTan: '山上有火，旅；君子以明慎用刑' },
  '巽': { guaCi: '小亨，利攸往，利见大人', tiTan: '随风，巽；君子以申命行事' },
  '兑': { guaCi: '亨利贞', tiTan: '丽泽，兑；君子以朋友讲习' },
  '涣': { guaCi: '亨，王假有庙，利涉大川，利贞', tiTan: '风行水上，涣；先王以享于帝立庙' },
  '节': { guaCi: '亨，苦节不可贞', tiTan: '泽上有水，节；君子以制数度' },
  '中孚': { guaCi: '豚鱼吉，利涉大川，利贞', tiTan: '泽上有风，中孚；君子以议狱缓死' },
  '小过': { guaCi: '亨，利贞，可小事，不可大事', tiTan: '山上有雷，小过；君子以行过乎恭' },
  '既济': { guaCi: '亨，小利贞，初吉终乱', tiTan: '水在火上，既济；君子以思患而豫防之' },
  '未济': { guaCi: '亨，小狐汔济，濡其尾，无攸利', tiTan: '火在水上，未济；君子以慎辨物居方' },
};

// ==================== 类型定义 ====================

export type YaoType = '老阳' | '少阳' | '老阴' | '少阴';

export interface Yao {
  position: number; // 1-6，从初爻到上爻
  name: string; // 爻名
  type: YaoType;
  isChanging: boolean;
  naJia: { stem: string; branch: string };
  fiveElement: string;
  sixRelative: string;
  sixBeast: string;
  isShi: boolean;
  isYing: boolean;
}

export interface Hexagram {
  name: string;
  upperTrigram: string;
  lowerTrigram: string;
  gua: string;
  isLiuShi: boolean;
  isLiuHe: boolean;
}

export interface HuGuaInfo {
  name: string;
  upperTrigram: string;
  lowerTrigram: string;
  gua: string;
  yaoList: Yao[];
  zhouYiText?: { guaCi: string; tiTan: string };
}

export interface GanZhi {
  year: { ganZhi: string; element: string; stem: string; branch: string };
  month: { ganZhi: string; element: string; stem: string; branch: string };
  day: { ganZhi: string; element: string; stem: string; branch: string };
  hour: { ganZhi: string; element: string; stem: string; branch: string };
}

export interface DivinationResult {
  originalHexagram: Hexagram;
  changedHexagram: Hexagram;
  huGua: HuGuaInfo;
  yaoList: Yao[];
  ganZhi: GanZhi;
  question: string;
  questionType: string;
  yongShen: Yao | undefined;
  yongShenName: string;
  zhouYiText?: { guaCi: string; tiTan: string };
  analysis: { title: string; content: string; level?: string }[];
  conclusion: string;
  directAnswer: string;
  suggestions: string[];
  timing: string;
}

// ==================== 核心算法 ====================

// 将爻转换为二进制
function yaoToBinary(type: YaoType): string {
  return (type === '老阳' || type === '少阳') ? '1' : '0';
}

// 获取卦名和上下卦
function getHexagramInfo(yaoTypes: YaoType[]): { name: string; upper: string; lower: string } {
  const lowerBinary = yaoToBinary(yaoTypes[0]) + yaoToBinary(yaoTypes[1]) + yaoToBinary(yaoTypes[2]);
  const upperBinary = yaoToBinary(yaoTypes[3]) + yaoToBinary(yaoTypes[4]) + yaoToBinary(yaoTypes[5]);

  const upper = EIGHT_TRIGRAMS[upperBinary]?.name || '未知';
  const lower = EIGHT_TRIGRAMS[lowerBinary]?.name || '未知';

  // 周易64卦序
  const trigramOrder = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤'];
  const hexagramNames: string[][] = [
    ['乾', '履', '同人', '无妄', '小畜', '需', '大畜', '泰'],
    ['夬', '履', '睽', '归妹', '中孚', '节', '损', '临'],
    ['大有', '睽', '离', '噬嗑', '旅', '未济', '贲', '晋'],
    ['大壮', '归妹', '噬嗑', '震', '恒', '解', '丰', '豫'],
    ['小畜', '中孚', '家人', '益', '巽', '涣', '蛊', '升'],
    ['需', '节', '既济', '屯', '井', '坎', '蹇', '比'],
    ['大畜', '贲', '颐', '蛊', '蒙', '蒙', '艮', '剥'],
    ['讼', '睽', '蛊', '豫', '益', '屯', '颐', '临'],
  ];

  const upperIndex = trigramOrder.indexOf(upper);
  const lowerIndex = trigramOrder.indexOf(lower);
  const name = (upperIndex >= 0 && lowerIndex >= 0) ? hexagramNames[upperIndex][lowerIndex] : upper + lower;

  return { name, upper, lower };
}

// 获取世应位置
function getShiYingPosition(hexagramName: string): { shi: number; ying: number } {
  const shiYingByPalace: Record<string, Record<string, { shi: number; ying: number }>> = {
    '乾宫': { '乾': { shi: 6, ying: 3 }, '姤': { shi: 1, ying: 4 }, '遁': { shi: 2, ying: 5 }, '否': { shi: 3, ying: 6 }, '观': { shi: 4, ying: 1 }, '剥': { shi: 5, ying: 2 } },
    '兑宫': { '履': { shi: 6, ying: 3 }, '兑': { shi: 3, ying: 6 }, '睽': { shi: 4, ying: 1 }, '归妹': { shi: 5, ying: 2 }, '中孚': { shi: 2, ying: 5 }, '节': { shi: 3, ying: 6 } },
    '离宫': { '同人': { shi: 2, ying: 5 }, '离': { shi: 5, ying: 2 }, '旅': { shi: 4, ying: 1 }, '鼎': { shi: 3, ying: 6 }, '未济': { shi: 5, ying: 2 }, '蒙': { shi: 4, ying: 1 } },
    '震宫': { '无妄': { shi: 6, ying: 3 }, '大壮': { shi: 4, ying: 1 }, '震': { shi: 6, ying: 3 }, '豫': { shi: 3, ying: 6 }, '解': { shi: 5, ying: 2 }, '恒': { shi: 6, ying: 3 } },
    '巽宫': { '小畜': { shi: 6, ying: 3 }, '中孚': { shi: 2, ying: 5 }, '巽': { shi: 1, ying: 4 }, '家人': { shi: 5, ying: 2 }, '益': { shi: 4, ying: 1 }, '蛊': { shi: 6, ying: 3 } },
    '坎宫': { '需': { shi: 3, ying: 6 }, '节': { shi: 2, ying: 5 }, '既济': { shi: 5, ying: 2 }, '坎': { shi: 5, ying: 2 }, '屯': { shi: 4, ying: 1 }, '蹇': { shi: 5, ying: 2 } },
    '艮宫': { '大畜': { shi: 3, ying: 6 }, '损': { shi: 2, ying: 5 }, '贲': { shi: 4, ying: 1 }, '颐': { shi: 3, ying: 6 }, '蛊': { shi: 6, ying: 3 }, '蒙': { shi: 2, ying: 5 } },
    '坤宫': { '泰': { shi: 3, ying: 6 }, '临': { shi: 2, ying: 5 }, '复': { shi: 6, ying: 3 }, '谦': { shi: 3, ying: 6 }, '坤': { shi: 6, ying: 3 }, '师': { shi: 1, ying: 4 } },
  };

  for (const palace of Object.values(shiYingByPalace)) {
    if (palace[hexagramName]) return palace[hexagramName];
  }
  return { shi: 3, ying: 6 };
}

// 纳甲装卦
function getNaJia(position: number, trigram: string): { stem: string; branch: string } {
  const naJiaConfig: Record<string, { stems: string[]; branches: string[] }> = {
    '乾': { stems: ['壬', '壬', '壬', '甲', '甲', '甲'], branches: ['子', '寅', '辰', '午', '申', '戌'] },
    '坤': { stems: ['癸', '癸', '癸', '乙', '乙', '乙'], branches: ['未', '巳', '卯', '丑', '亥', '酉'] },
    '震': { stems: ['庚', '庚', '庚', '庚', '庚', '庚'], branches: ['子', '寅', '辰', '午', '申', '戌'] },
    '巽': { stems: ['辛', '辛', '辛', '辛', '辛', '辛'], branches: ['丑', '亥', '酉', '未', '巳', '卯'] },
    '坎': { stems: ['戊', '戊', '戊', '戊', '戊', '戊'], branches: ['寅', '辰', '午', '申', '戌', '子'] },
    '离': { stems: ['己', '己', '己', '己', '己', '己'], branches: ['卯', '巳', '未', '酉', '亥', '丑'] },
    '艮': { stems: ['丙', '丙', '丙', '丙', '丙', '丙'], branches: ['辰', '午', '申', '戌', '子', '寅'] },
    '兑': { stems: ['丁', '丁', '丁', '丁', '丁', '丁'], branches: ['巳', '未', '酉', '亥', '丑', '卯'] },
  };

  const config = naJiaConfig[trigram] || naJiaConfig['乾'];
  return { stem: config.stems[position - 1], branch: config.branches[position - 1] };
}

// 获取六亲
function getSixRelative(stem: string, trigramElement: string): string {
  const stemElement = FIVE_ELEMENTS[stem]?.element || '';
  if (stemElement === trigramElement) return '兄弟';
  if (ELEMENT_BATTLE[stemElement]?.includes(trigramElement)) return '妻财';
  if (ELEMENT_BATTLE[trigramElement]?.includes(stemElement)) return '官鬼';
  if (ELEMENT_BIRTH[stemElement]?.includes(trigramElement)) return '子孙';
  if (ELEMENT_BIRTH[trigramElement]?.includes(stemElement)) return '父母';
  return '兄弟';
}

// 获取六神
function getSixBeast(position: number, dayBranch: string): string {
  const dayBranchIndex = EARTHLY_BRANCHES.indexOf(dayBranch);
  const startIndex = (dayBranchIndex + 1) % 6;
  return SIX_BEASTS[(startIndex + position - 1) % 6];
}

// 判断六冲卦
function isLiuShiHexagram(hexagramName: string): boolean {
  return ['乾', '坤', '坎', '离', '震', '巽', '艮', '兑', '无妄', '大壮', '遁', '临', '讼', '睽', '萃'].includes(hexagramName);
}

// 判断六合卦
function isLiuHeHexagram(hexagramName: string): boolean {
  return ['泰', '否', '咸', '恒', '既济', '未济', '家人', '睽', '蹇', '解', '蛊', '井', '困', '贲'].includes(hexagramName);
}

// 判断问题类型
function determineQuestionType(question: string): { type: string; yongShen: string; description: string } {
  const q = question.toLowerCase();

  if (q.includes('考试') || q.includes('功名') || q.includes('升学') || q.includes('升职')) {
    return { type: '求名', yongShen: '官鬼', description: '占求名以官鬼爻为用神' };
  }
  if (q.includes('求财') || q.includes('财运') || q.includes('生意') || q.includes('投资')) {
    return { type: '求财', yongShen: '妻财', description: '占求财以妻财爻为用神' };
  }
  if (q.includes('病') || q.includes('健康') || q.includes('身体')) {
    return { type: '疾病', yongShen: '官鬼', description: '占病以官鬼爻为用神' };
  }
  if (q.includes('忧虑') || q.includes('担忧') || q.includes('烦恼')) {
    return { type: '忧虑', yongShen: '子孙', description: '占忧虑以子孙爻为用神' };
  }
  if (q.includes('婚姻') || q.includes('感情') || q.includes('恋爱') || q.includes('姻缘')) {
    return { type: '婚姻', yongShen: '妻财', description: '占婚姻以妻财爻（男）或官鬼爻（女）为用神' };
  }
  if (q.includes('出行') || q.includes('旅行') || q.includes('搬迁')) {
    return { type: '出行', yongShen: '父母', description: '占出行以父母爻为用神' };
  }
  if (q.includes('诉讼') || q.includes('官司') || q.includes('是非')) {
    return { type: '官讼', yongShen: '官鬼', description: '占官讼以官鬼爻为用神' };
  }
  if (q.includes('流年') || q.includes('今年') || q.includes('明年')) {
    return { type: '流年', yongShen: '世爻', description: '占流年以世爻为主参看六亲' };
  }
  return { type: '一般', yongShen: '世爻', description: '此类事宜以世爻为主进行判断' };
}

// 获取变卦
function getChangedHexagram(yaoTypes: YaoType[]): { name: string; upper: string; lower: string } {
  const changedTypes = yaoTypes.map(type => {
    if (type === '老阳') return '少阴' as YaoType;
    if (type === '老阴') return '少阳' as YaoType;
    return type;
  });
  return getHexagramInfo(changedTypes);
}

// 获取互卦
function getHuGuayInfo(yaoTypes: YaoType[]): { name: string; upper: string; lower: string } {
  const huLower = [yaoTypes[1], yaoTypes[2], yaoTypes[3]];
  const huUpper = [yaoTypes[2], yaoTypes[3], yaoTypes[4]];

  const lowerBinary = huLower.map(yao => yaoToBinary(yao)).join('');
  const upperBinary = huUpper.map(yao => yaoToBinary(yao)).join('');

  const upper = EIGHT_TRIGRAMS[upperBinary]?.name || '未知';
  const lower = EIGHT_TRIGRAMS[lowerBinary]?.name || '未知';

  const trigramOrder = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤'];
  const hexagramNames: string[][] = [
    ['乾', '履', '同人', '无妄', '小畜', '需', '大畜', '泰'],
    ['夬', '履', '睽', '归妹', '中孚', '节', '损', '临'],
    ['大有', '睽', '离', '噬嗑', '旅', '未济', '贲', '晋'],
    ['大壮', '归妹', '噬嗑', '震', '恒', '解', '丰', '豫'],
    ['小畜', '中孚', '家人', '益', '巽', '涣', '蛊', '升'],
    ['需', '节', '既济', '屯', '井', '坎', '蹇', '比'],
    ['大畜', '贲', '颐', '蛊', '蒙', '蒙', '艮', '剥'],
    ['讼', '睽', '蛊', '豫', '益', '屯', '颐', '临'],
  ];

  const upperIndex = trigramOrder.indexOf(upper);
  const lowerIndex = trigramOrder.indexOf(lower);
  const name = (upperIndex >= 0 && lowerIndex >= 0) ? hexagramNames[upperIndex][lowerIndex] : upper + lower;

  return { name, upper, lower };
}

// 获取爻的名称
function getYaoName(position: number): string {
  const names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
  return names[position - 1];
}

// 解析干支信息
export function parseGanZhi(yearStem: string, yearBranch: string, monthStem: string, monthBranch: string, dayStem: string, dayBranch: string, hourStem: string, hourBranch: string): GanZhi {
  const parse = (stem: string, branch: string) => ({
    ganZhi: stem + branch,
    element: FIVE_ELEMENTS[stem]?.element || '',
    stem,
    branch,
  });

  return {
    year: parse(yearStem, yearBranch),
    month: parse(monthStem, monthBranch),
    day: parse(dayStem, dayBranch),
    hour: parse(hourStem, hourBranch),
  };
}

// 主测算函数
export function calculateDivination(yaoTypes: YaoType[], question: string, ganZhi: GanZhi): DivinationResult {
  if (yaoTypes.length !== 6) {
    throw new Error('需要输入6个爻');
  }

  // 获取卦名
  const originalHex = getHexagramInfo(yaoTypes);
  const changedHex = getChangedHexagram(yaoTypes);
  const { shi, ying } = getShiYingPosition(originalHex.name);

  // 构造卦象信息
  const hexagram: Hexagram = {
    name: originalHex.name,
    upperTrigram: originalHex.upper,
    lowerTrigram: originalHex.lower,
    gua: `${EIGHT_TRIGRAMS[yaoTypes.slice(3, 6).map(yao => yaoToBinary(yao)).join('')]?.gua || '☷'}${EIGHT_TRIGRAMS[yaoTypes.slice(0, 3).map(yao => yaoToBinary(yao)).join('')]?.gua || '☰'}`,
    isLiuShi: isLiuShiHexagram(originalHex.name),
    isLiuHe: isLiuHeHexagram(originalHex.name),
  };

  const changedHexagram: Hexagram = {
    name: changedHex.name,
    upperTrigram: changedHex.upper,
    lowerTrigram: changedHex.lower,
    gua: `${EIGHT_TRIGRAMS[yaoTypes.slice(3, 6).map(yao => {
      const changed = yao === '老阳' ? '少阴' : yao === '老阴' ? '少阳' : yao;
      return yaoToBinary(changed);
    }).join('')]?.gua || '☷'}${EIGHT_TRIGRAMS[yaoTypes.slice(0, 3).map(yao => {
      const changed = yao === '老阳' ? '少阴' : yao === '老阴' ? '少阳' : yao;
      return yaoToBinary(changed);
    }).join('')]?.gua || '☰'}`,
    isLiuShi: isLiuShiHexagram(changedHex.name),
    isLiuHe: isLiuHeHexagram(changedHex.name),
  };

  // 计算互卦
  const huGuaInfo = getHuGuayInfo(yaoTypes);
  const huGuaZhouYiText = ZHOU_YI_HEXAGRAM_TEXTS[huGuaInfo.name] || { guaCi: '卦辞不详', tiTan: '象传不详' };
  const huGua: HuGuaInfo = {
    name: huGuaInfo.name,
    upperTrigram: huGuaInfo.upper,
    lowerTrigram: huGuaInfo.lower,
    gua: `${EIGHT_TRIGRAMS[Object.entries(EIGHT_TRIGRAMS).find(([k, v]) => v.name === huGuaInfo.upper)?.[0] || '000']?.gua || '☷'}${EIGHT_TRIGRAMS[Object.entries(EIGHT_TRIGRAMS).find(([k, v]) => v.name === huGuaInfo.lower)?.[0] || '000']?.gua || '☰'}`,
    yaoList: [],
    zhouYiText: huGuaZhouYiText,
  };

  // 确定问题类型和用神
  const questionInfo = determineQuestionType(question);

  // 构造爻列表
  const yaoList: Yao[] = yaoTypes.map((type, index) => {
    const position = index + 1;
    const trigram = position > 3 ? originalHex.upper : originalHex.lower;
    const trigramElement = EIGHT_TRIGRAMS[Object.entries(EIGHT_TRIGRAMS).find(([k, v]) => v.name === trigram)?.[0] || '000']?.element || '土';
    const naJia = getNaJia(position, trigram);
    const fiveElement = FIVE_ELEMENTS[naJia.stem]?.element || '';
    const sixRelative = getSixRelative(naJia.stem, trigramElement);
    const sixBeast = getSixBeast(position, ganZhi.day.branch);

    return {
      position,
      name: getYaoName(position),
      type,
      isChanging: type === '老阳' || type === '老阴',
      naJia,
      fiveElement,
      sixRelative,
      sixBeast,
      isShi: position === shi,
      isYing: position === ying,
    };
  });

  // 获取用神
  const yongShen = yaoList.find(yao => {
    if (questionInfo.yongShen === '世爻') return yao.isShi;
    return yao.sixRelative === questionInfo.yongShen;
  });

  // 分析卦象
  const shiYao = yaoList.find(yao => yao.isShi)!;
  const shiRelative = shiYao.sixRelative;
  const changingYao = yaoList.filter(yao => yao.isChanging);

  // 生成分析结果
  const analysis: { title: string; content: string; level?: string }[] = [];

  analysis.push({
    title: '一、卦象概述',
    content: `本卦为${originalHex.name}卦${hexagram.isLiuShi ? '（六冲卦，主事速成但多变）' : ''}${hexagram.isLiuHe ? '（六合卦，主事迟缓但有情）' : ''}，变卦为${changedHex.name}卦。`
  });

  if (changingYao.length > 0) {
    const changeInfo = changingYao.map(yao => `${yao.name}(${yao.type}化${yao.type === '老阳' ? '少阴' : '少阳'})`).join('，');
    analysis.push({
      title: '二、动爻分析',
      content: `动爻为${changingYao.length}个：${changeInfo}。动则变，化出之爻对卦象有重要影响。`
    });
  } else {
    analysis.push({
      title: '二、动爻分析',
      content: '此卦为静卦，无动爻。静卦以世爻、用神为主进行判断。'
    });
  }

  // 用神分析
  analysis.push({
    title: '三、用神分析',
    content: `用神为${questionInfo.yongShen}爻${yongShen ? `，${yongShen.name}${yongShen.naJia.stem}${yongShen.naJia.branch}${yongShen.isShi ? '持世' : '持应'}` : '。'}`
  });

  // 吉凶判断
  let directAnswer = '';
  let conclusion = '';
  const suggestions: string[] = [];
  let timing = '';

  switch (questionInfo.type) {
    case '求名':
      if (shiRelative === '官鬼') {
        directAnswer = '✅ 可以通过考试';
        conclusion = `本卦${originalHex.name}，世爻为官鬼爻持世。《增删卜易》明示："占功名者，若得官鬼持世即许成名。"功名可成！`;
        suggestions.push('宜积极备考，把握良机');
        suggestions.push('官鬼持世，此番考试必有所成');
      } else if (shiRelative === '子孙') {
        directAnswer = '❌ 此次难以通过，需另寻他途';
        conclusion = `本卦${originalHex.name}，子孙爻持世。《增删卜易》云："子孙持世，自首无成。"子孙克制官鬼，功名难得。`;
        suggestions.push('宜静待时机，不宜强求');
        suggestions.push('可另寻他途，或蓄势待发');
      } else {
        directAnswer = '⚠️ 结果待定，需综合判断';
        conclusion = `本卦${originalHex.name}，世爻为${shiRelative}，吉凶需综合判断。`;
      }
      break;

    case '求财':
      if (shiRelative === '妻财') {
        directAnswer = '✅ 可以得财，财运亨通';
        conclusion = `本卦${originalHex.name}，妻财持世。《增删卜易》明示："财星持世，不日即可获得。"`;
        suggestions.push('把握良机，积极进取');
      } else if (shiRelative === '兄弟') {
        directAnswer = '❌ 难以得财，恐有破耗';
        conclusion = `本卦${originalHex.name}，兄弟持世。《增删卜易》明示："兄弟持世者难求。"`;
        suggestions.push('不宜投资，守成为上');
      } else {
        directAnswer = '⚠️ 财运一般';
        conclusion = `本卦${originalHex.name}，世爻为${shiRelative}，财运一般。`;
      }
      break;

    case '疾病':
      if (shiRelative === '子孙') {
        directAnswer = '✅ 疾病可愈，身体无忧';
        conclusion = `本卦${originalHex.name}，子孙持世。《增删卜易》明示："子孙持世者易安。"`;
        suggestions.push('安心调养，定能康复');
      } else if (shiRelative === '官鬼') {
        directAnswer = '❌ 病情需谨慎，及时医治';
        conclusion = `本卦${originalHex.name}，官鬼持世。《增删卜易》明示："官鬼持世者难愈。"`;
        suggestions.push('及时医治，不可拖延');
      } else if (hexagram.isLiuShi) {
        directAnswer = '⚠️ 近病可愈，久病需调养';
        conclusion = `本卦${originalHex.name}为六冲卦。《增删卜易》明示："六冲卦，近病不药而愈，久病妙药难调。"`;
      } else {
        directAnswer = '⚠️ 吉凶参半，需积极医治';
        conclusion = `本卦${originalHex.name}，世爻为${shiRelative}，需结合医嘱调养。`;
      }
      break;

    default:
      directAnswer = '⚠️ 需综合分析';
      conclusion = `本卦${originalHex.name}，世爻为${shiRelative}，尚需结合具体事宜综合分析。`;
  }

  // 应期判断
  if (changingYao.length > 0) {
    const avgPos = changingYao.reduce((a, b) => a + b.position, 0) / changingYao.length;
    if (avgPos <= 2) timing = '应期在近日（三日之内），或逢生合世爻之日月应验。';
    else if (avgPos <= 4) timing = '应期在近期（七日之内），或逢冲开之年月日应验。';
    else timing = '应期在一月之内，待时机成熟方能应验。';
  } else {
    timing = '此为静卦，应期需看世爻旺衰，旺则速，衰则缓。';
  }

  // 获取周易卦辞
  const zhouYiText = ZHOU_YI_HEXAGRAM_TEXTS[originalHex.name] || { guaCi: '卦辞不详', tiTan: '象传不详' };

  return {
    originalHexagram: hexagram,
    changedHexagram,
    huGua,
    yaoList,
    ganZhi,
    question,
    questionType: questionInfo.type,
    yongShen,
    yongShenName: questionInfo.description,
    zhouYiText,
    analysis,
    conclusion,
    directAnswer,
    suggestions,
    timing,
  };
}

// 辅助函数：获取爻符号
export function getYaoSymbol(type: YaoType): string {
  const symbols: Record<YaoType, string> = {
    '老阳': '○',
    '少阳': '—',
    '老阴': '×',
    '少阴': '--',
  };
  return symbols[type];
}
