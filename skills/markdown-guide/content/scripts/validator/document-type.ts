/**
 * 文档类型识别与标准格式校验模块
 * 
 * 包含文档类型自动识别、格式标准校验、必选/可选章节检查
 */

import {
  BaseValidator,
  DocumentType,
  DocumentTypePattern,
  DocumentStandardResult,
  StandardCheck
} from './core';

// ============== 文档类型模式定义 ==============

const DOCUMENT_PATTERNS: DocumentTypePattern[] = [
  {
    type: 'readme',
    patterns: [
      /^readme\.md$/i,
      /^#\s+(.+)\s*\n.*(?:安装|install|快速开始|quick\s*start)/im,
    ],
    requiredSections: ['安装', '使用', '许可证'],
    optionalSections: ['贡献', '变更日志', '常见问题'],
    priority: 10
  },
  {
    type: 'api-documentation',
    patterns: [
      /api.*\.md$/i,
      /#\s*API\s*(文档|documentation|reference)/i,
      /##\s*(endpoints?|接口|路由)/i,
    ],
    requiredSections: ['接口列表', '认证', '错误码'],
    optionalSections: ['速率限制', '版本控制', '示例'],
    priority: 9
  },
  {
    type: 'faq',
    patterns: [
      /faq\.md$/i,
      /^#\s*(faq|frequently\s*asked|常见问题)/im,
      /##\s*(q:|question|问题)/i,
    ],
    requiredSections: [],
    optionalSections: ['概述', '分类', '反馈'],
    priority: 9
  },
  {
    type: 'technical-guide',
    patterns: [
      /guide\.md$/i,
      /tutorial\.md$/i,
      /#\s*(指南|guide|教程|tutorial)/i,
      /##\s*(步骤|step|教程|介绍|overview)/i,
    ],
    requiredSections: [],  // 技术指南结构灵活，不强制必选章节
    optionalSections: ['概述', '步骤', '总结', '前置条件', '常见问题', '进阶'],
    priority: 8
  },
  {
    type: 'changelog',
    patterns: [
      /changelog\.md$/i,
      /changes\.md$/i,
      /^#\s*(changelog|变更日志|更新日志)/im,
      /^##\s*\[?\d+\.\d+/im,
    ],
    requiredSections: [],
    optionalSections: ['未发布', '版本历史'],
    priority: 7
  },
  {
    type: 'contributing',
    patterns: [
      /contributing\.md$/i,
      /^#\s*(contributing|贡献指南)/im,
      /##\s*(开发环境|development\s*environment)/i,
    ],
    requiredSections: ['如何贡献'],  // 只强制"如何贡献"
    optionalSections: ['代码规范', '提交规范', '项目结构', '测试', '发布流程'],
    priority: 6
  },
  {
    type: 'design-doc',
    patterns: [
      /design.*\.md$/i,
      /rfc.*\.md$/i,
      /需求文档\.md$/i,
      /架构.*\.md$/i,
      /^#\s*(设计文档|design\s*doc|rfc|需求文档|系统.*文档)/im,
      /##\s*(背景|background|目标|objectives|系统概述|架构)/i,
    ],
    requiredSections: ['背景', '目标', '方案设计'],
    optionalSections: ['替代方案', '风险评估', '时间线'],
    priority: 11
  },
  {
    type: 'workflow-doc',
    patterns: [
      /交互流程.*\.md$/i,
      /流程.*\.md$/i,
      /workflow.*\.md$/i,
      /^#\s*(交互流程|流程描述|工作流)/im,
      /##\s*(流程|描述|步骤)/i,
    ],
    requiredSections: ['描述', '流程'],
    optionalSections: ['前置条件', '错误说明', '状态说明'],
    priority: 12
  },
  {
    type: 'specification',
    patterns: [
      /规范.*\.md$/i,
      /spec.*\.md$/i,
      /standard.*\.md$/i,
      /^#\s*(规范|specification|标准)/im,
      /##\s*(规范说明|适用范围|定义)/i,
    ],
    requiredSections: ['概述', '规范说明'],
    optionalSections: ['适用范围', '参考文档', '修订历史'],
    priority: 12
  },
  {
    type: 'man-page',
    patterns: [
      /^_[A-Z]+\.md$/i,  // _AUTHORS.md, _OPTIONS.md 等格式
      /^#\s+[A-Z]+\s*$/im,  // # AUTHORS, # OPTIONS 等
      /##\s*(synopsis|description|options|files|bugs)/i,
    ],
    requiredSections: [],
    optionalSections: ['作者', '参见', '历史'],
    priority: 13
  },
  {
    type: 'user-documentation',
    patterns: [
      /user.*doc.*\.md$/i,
      /用户.*文档.*\.md$/i,
      /^#\s*(用户文档|user\s*document|用户指南)/im,
    ],
    requiredSections: ['概述', '功能说明'],
    optionalSections: ['快速开始', '常见问题', '术语表'],
    priority: 10
  },
  {
    type: 'quickstart',
    patterns: [
      /quickstart\.md$/i,
      /快速开始\.md$/i,
      /^#\s*(quickstart|快速开始|入门)/im,
    ],
    requiredSections: ['概述'],
    optionalSections: ['安装', '示例', '下一步'],
    priority: 9
  },
];

export class DocumentTypeValidator extends BaseValidator {
  private detectedType: DocumentType = 'unknown';
  private confidence: number = 0;
  private standardChecks: StandardCheck[] = [];

  validate(): void {
    this.detectDocumentType();
    this.checkDocumentStandards();
  }

  getResult(): DocumentStandardResult {
    const requiredPassed = this.standardChecks.filter(
      c => c.importance === 'required' && c.passed
    ).length;
    const requiredTotal = this.standardChecks.filter(
      c => c.importance === 'required'
    ).length;

    const recommendedPassed = this.standardChecks.filter(
      c => c.importance === 'recommended' && c.passed
    ).length;
    const recommendedTotal = this.standardChecks.filter(
      c => c.importance === 'recommended'
    ).length;

    const requiredScore = requiredTotal > 0 ? requiredPassed / requiredTotal : 1;
    const recommendedScore = recommendedTotal > 0 ? recommendedPassed / recommendedTotal : 1;

    const overallScore = (requiredScore * 0.7 + recommendedScore * 0.3) * 100;

    const missingSections = this.standardChecks
      .filter(c => c.importance === 'required' && !c.passed)
      .map(c => c.rule.replace('section-', ''));

    const suggestedSections = this.standardChecks
      .filter(c => c.importance === 'recommended' && !c.passed)
      .map(c => c.rule.replace('section-', ''));

    return {
      detectedType: this.detectedType,
      confidence: this.confidence,
      standardChecks: this.standardChecks,
      overallScore,
      missingSections,
      suggestedSections
    };
  }

  // ============== 文档类型识别 ==============

  private detectDocumentType(): void {
    const fileName = this.filePath.split('/').pop() || '';
    const content = this.content;

    const scores: Map<DocumentType, number> = new Map();

    DOCUMENT_PATTERNS.forEach(pattern => {
      let score = 0;

      pattern.patterns.forEach(p => {
        if (p.test(fileName) || p.test(content)) {
          score += pattern.priority;
        }
      });

      if (score > 0) {
        scores.set(pattern.type, score);
      }
    });

    let maxScore = 0;
    scores.forEach((score, type) => {
      if (score > maxScore) {
        maxScore = score;
        this.detectedType = type;
      }
    });

    this.confidence = maxScore > 0 ? Math.min(maxScore / 20, 1) : 0;

    if (this.detectedType === 'unknown') {
      this.detectedType = this.inferTypeFromContent();
    }
  }

  private inferTypeFromContent(): DocumentType {
    const headings = this.lines
      .filter(l => /^#{1,2}\s/.test(l))
      .map(l => l.replace(/^#+\s+/, '').toLowerCase());

    if (headings.some(h => /api|接口|endpoint/i.test(h))) {
      return 'api-documentation';
    }

    if (headings.some(h => /步骤|step|教程|tutorial/i.test(h))) {
      return 'technical-guide';
    }

    if (headings.some(h => /安装|install|使用|usage/i.test(h))) {
      return 'readme';
    }

    return 'unknown';
  }

  // ============== 文档标准校验 ==============

  private checkDocumentStandards(): void {
    const pattern = DOCUMENT_PATTERNS.find(p => p.type === this.detectedType);

    if (!pattern) {
      return;
    }

    const existingSections = this.extractSections();

    pattern.requiredSections.forEach(section => {
      const exists = existingSections.some(s =>
        this.sectionsMatch(s, section)
      );

      this.standardChecks.push({
        rule: `section-${section}`,
        passed: exists,
        message: exists
          ? `必选章节"${section}"存在`
          : `缺少必选章节"${section}"`,
        importance: 'required'
      });

      if (!exists) {
        this.addError(
          1,
          'missing-required-section',
          `缺少必选章节: ${section}`,
          `添加章节: ## ${section}`
        );
      }
    });

    pattern.optionalSections.forEach(section => {
      const exists = existingSections.some(s =>
        this.sectionsMatch(s, section)
      );

      this.standardChecks.push({
        rule: `section-${section}`,
        passed: exists,
        message: exists
          ? `推荐章节"${section}"存在`
          : `缺少推荐章节"${section}"`,
        importance: 'recommended'
      });

      if (!exists) {
        this.addInfo(
          1,
          'missing-recommended-section',
          `建议添加章节: ${section}`,
          `添加章节: ## ${section}`
        );
      }
    });

    this.checkDocumentStructure();
  }

  private extractSections(): string[] {
    const sections: string[] = [];

    this.lines.forEach(line => {
      // 处理 CRLF 和 LF 换行符
      const cleanLine = line.replace(/\r/g, '');
      const match = cleanLine.match(/^#{1,2}\s+(.+)$/);
      if (match) {
        sections.push(match[1].trim().toLowerCase());
      }
    });

    return sections;
  }

  private sectionsMatch(actual: string, expected: string): boolean {
    const normalize = (s: string) => s.toLowerCase().replace(/[\s-_]/g, '');

    const normalizedActual = normalize(actual);
    const normalizedExpected = normalize(expected);

    if (normalizedActual.includes(normalizedExpected)) return true;
    if (normalizedExpected.includes(normalizedActual)) return true;

    // 双向翻译映射：支持中英文互查
    const translations: Record<string, string[]> = {
      // README 相关
      '安装': ['install', 'installation', 'installing', 'setup'],
      '使用': ['usage', 'use', 'using', 'getting started'],
      '许可证': ['license', 'licensing'],
      '贡献': ['contributing', 'contribute', 'contribution'],
      '变更日志': ['changelog', 'changes', 'history', 'release notes'],
      '常见问题': ['faq', 'frequently asked', 'questions'],
      // API 文档相关
      '接口列表': ['endpoints', 'endpoint', 'api reference', 'apis', 'routes'],
      '认证': ['authentication', 'auth', 'authorization'],
      '错误码': ['error codes', 'errors', 'error handling', 'error response'],
      '速率限制': ['rate limiting', 'rate limit', 'throttling'],
      '版本控制': ['versioning', 'version', 'versions'],
      '示例': ['examples', 'example', 'samples', 'sample'],
      // 设计文档相关
      '背景': ['background', 'context', '背景介绍', '系统概述', '概述', '前言', '引言', 'introduction'],
      '目标': ['objectives', 'goals', '目标', '目的', '设计目标', '系统目标', '核心目标'],
      '方案设计': ['solution design', 'design', '方案', '架构设计', '系统设计', '详细设计', '系统架构', '架构'],
      '系统概述': ['system overview', 'overview', '概述'],
      '架构': ['architecture', '系统架构'],
      // 用户文档相关
      '功能说明': ['功能', 'features', '功能介绍', 'feature description', 'use cases'],
      // 流程文档相关
      '描述': ['description', '说明', '简介', '概述'],
      '流程': ['flow', 'workflow', '步骤', 'procedure', 'process', 'steps'],
      '前置条件': ['prerequisites', '前置要求', '前提条件'],
      '错误说明': ['errors', '错误处理', '错误码', 'error handling'],
      '状态说明': ['states', '状态', '状态定义', 'status'],
      // 英文 -> 中文反向映射
      'install': ['安装', 'installation'],
      'usage': ['使用'],
      'license': ['许可证'],
      'contributing': ['贡献'],
      'changelog': ['变更日志', '更新日志'],
      'faq': ['常见问题'],
      'endpoints': ['接口列表', '接口'],
      'authentication': ['认证'],
      'errors': ['错误码', '错误'],
      'examples': ['示例'],
      'background': ['背景'],
      'objectives': ['目标'],
      'design': ['方案设计', '设计'],
      'introduction': ['概述', '背景', '引言', '前言'],
      'features': ['功能说明', '功能'],
    };

    // 直接匹配 expected key
    const expectedLower = expected.toLowerCase();
    if (translations[expected]) {
      return translations[expected].some(t =>
        normalizedActual.includes(normalize(t))
      );
    }

    // 尝试 normalizedExpected 作为 key
    if (translations[normalizedExpected]) {
      return translations[normalizedExpected].some(t =>
        normalizedActual.includes(normalize(t))
      );
    }

    // 尝试 actual 作为 key（反向查找）
    if (translations[normalizedActual]) {
      return translations[normalizedActual].some(t =>
        normalizedExpected.includes(normalize(t))
      );
    }

    // 模糊匹配：检查是否有部分匹配
    for (const [key, values] of Object.entries(translations)) {
      if (normalizedExpected.includes(normalize(key)) || normalize(key).includes(normalizedExpected)) {
        if (values.some(v => normalizedActual.includes(normalize(v)))) {
          return true;
        }
      }
    }

    return false;
  }

  private checkDocumentStructure(): void {
    const headings = this.lines
      .map((line, index) => {
        const match = line.match(/^(#{1,6})\s+(.+)$/);
        if (match) {
          return {
            level: match[1].length,
            text: match[2].trim(),
            line: index + 1
          };
        }
        return null;
      })
      .filter(h => h !== null) as Array<{ level: number; text: string; line: number }>;

    if (headings.length === 0) {
      this.addWarning(1, 'no-headings', '文档没有任何标题', '添加标题组织文档内容');
      return;
    }

    const firstHeading = headings[0];
    if (firstHeading.level !== 1) {
      this.addWarning(
        firstHeading.line,
        'first-heading-not-h1',
        '文档第一个标题应为 H1',
        '将第一个标题改为 H1 级别'
      );
    }

    const h1Headings = headings.filter(h => h.level === 1);
    if (h1Headings.length > 1) {
      this.addWarning(
        h1Headings[1].line,
        'multiple-h1',
        '文档包含多个 H1 标题',
        '建议只保留一个 H1 标题作为文档主标题'
      );
    }

    let prevLevel = 0;
    headings.forEach(heading => {
      if (heading.level > prevLevel + 1 && prevLevel > 0) {
        this.addWarning(
          heading.line,
          'heading-level-skip',
          `标题层级跳跃: H${prevLevel} -> H${heading.level}`,
          `建议在 H${prevLevel} 和 H${heading.level} 之间添加 H${prevLevel + 1}`
        );
      }
      prevLevel = heading.level;
    });
  }
}
