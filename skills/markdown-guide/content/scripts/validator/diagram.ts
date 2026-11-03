/**
 * 图表校验模块
 * 
 * 包含 Mermaid、PlantUML、ASCII 艺术图表的语法校验和实体提取
 */

import { BaseValidator, EntityRegistry, DiagramRegistry, DiagramInfo, DiagramCompleteness, createEmptyDiagramRegistry, createEmptyDiagramCompleteness } from './core';

export class DiagramValidator extends BaseValidator {
  private entityRegistry: EntityRegistry;
  private diagramRegistry: DiagramRegistry;

  constructor(content: string, filePath: string, entityRegistry: EntityRegistry) {
    super(content, filePath);
    this.entityRegistry = entityRegistry;
    this.diagramRegistry = createEmptyDiagramRegistry();
  }

  validate(): void {
    this.checkMermaidDiagrams();
    this.checkPlantUmlDiagrams();
    this.checkAsciiArtDiagrams();
  }

  getDiagramRegistry(): DiagramRegistry {
    return this.diagramRegistry;
  }

  getEntityRegistry(): EntityRegistry {
    return this.entityRegistry;
  }

  // ============== Mermaid 图表校验 ==============

  private checkMermaidDiagrams(): void {
    const mermaidBlocks = this.extractCodeBlocks('mermaid');

    mermaidBlocks.forEach(block => {
      const { content, startLine } = block;

      const diagramTypes = [
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
        'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'gantt', 'pie', 'mindmap',
        'journey', 'gitGraph', 'C4Context', 'requirementDiagram',
        'swimlane', 'timeline', 'quadrantChart', 'xychart-beta', 'block-beta'
      ];

      const hasValidType = diagramTypes.some(type =>
        content.toLowerCase().includes(type.toLowerCase())
      );

      // 检查是否是 ASCII 艺术图（用 mermaid 代码块包裹但不是真正的 mermaid）
      const isAsciiArt = /^[+\-=|[\]{}]/m.test(content) && !hasValidType;

      if (!hasValidType && !isAsciiArt) {
        this.addError(
          startLine,
          'mermaid-invalid-type',
          'Mermaid 图表缺少有效的图表类型声明',
          '添加图表类型声明，如 graph TD、sequenceDiagram'
        );
      } else if (isAsciiArt) {
        this.addInfo(
          startLine,
          'mermaid-ascii-art',
          '此代码块包含 ASCII 艺术图而非 Mermaid 图表',
          '如需真正的 Mermaid 图表，请使用正确的图表类型声明'
        );
      }

      this.checkMermaidSyntax(content, startLine);
      this.extractMermaidEntities(content, startLine);
    });
  }

  private checkMermaidSyntax(content: string, startLine: number): void {
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      const quotes = (line.match(/"/g) || []).length;
      if (quotes % 2 !== 0) {
        this.addWarning(
          startLine + index + 1,
          'mermaid-unclosed-quote',
          'Mermaid 语句中存在未闭合的引号',
          '检查引号是否成对出现'
        );
      }
    });
  }

  private extractMermaidEntities(content: string, startLine: number): void {
    const classPattern = /class\s+(\w+)/g;
    let match;
    while ((match = classPattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'class', 'mermaid', startLine);
    }

    const participantPattern = /participant\s+(\w+)/g;
    while ((match = participantPattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'actor', 'mermaid', startLine);
    }

    const actorPattern = /actor\s+(\w+)/g;
    while ((match = actorPattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'actor', 'mermaid', startLine);
    }

    const statePattern = /(\w+)\s*-->/g;
    while ((match = statePattern.exec(content)) !== null) {
      if (match[1] !== '[*]' && match[1] !== 'stateDiagram') {
        this.registerEntity(match[1], 'state', 'mermaid', startLine);
      }
    }
  }

  // ============== PlantUML 图表校验 ==============

  private checkPlantUmlDiagrams(): void {
    const plantumlBlocks = this.extractCodeBlocks('plantuml');

    plantumlBlocks.forEach(block => {
      const { content, startLine } = block;

      const hasStart = content.includes('@startuml');
      const hasEnd = content.includes('@enduml');

      if (hasStart && !hasEnd) {
        this.addError(
          startLine,
          'plantuml-unclosed',
          'PlantUML 图表缺少 @enduml 标记',
          '在图表末尾添加 @enduml'
        );
      } else if (!hasStart && hasEnd) {
        this.addError(
          startLine,
          'plantuml-missing-start',
          'PlantUML 图表缺少 @startuml 标记',
          '在图表开头添加 @startuml'
        );
      }

      this.extractPlantUmlEntities(content, startLine);
    });
  }

  private extractPlantUmlEntities(content: string, startLine: number): void {
    const classPattern = /class\s+(\w+)/g;
    let match;
    while ((match = classPattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'class', 'plantuml', startLine);
    }

    const actorPattern = /actor\s+"?(\w+)"?/g;
    while ((match = actorPattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'actor', 'plantuml', startLine);
    }

    const participantPattern = /participant\s+"?(\w+)"?/g;
    while ((match = participantPattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'actor', 'plantuml', startLine);
    }

    const statePattern = /state\s+"?(\w+)"?/g;
    while ((match = statePattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'state', 'plantuml', startLine);
    }

    const entityPattern = /entity\s+"?(\w+)"?/g;
    while ((match = entityPattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'table', 'plantuml', startLine);
    }

    const usecasePattern = /usecase\s+"?([^"\n]+)"?/g;
    while ((match = usecasePattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'usecase', 'plantuml', startLine);
    }

    const componentPattern = /component\s+"?(\w+)"?/g;
    while ((match = componentPattern.exec(content)) !== null) {
      this.registerEntity(match[1], 'component', 'plantuml', startLine);
    }
  }

  // ============== ASCII 艺术图表校验 ==============

  private checkAsciiArtDiagrams(): void {
    // 更严格的 ASCII 艺术模式：需要多个特征组合才判定为图表
    // 避免将普通文本中的单个符号误判
    const asciiPatterns = [
      { pattern: /\+[-]{3,}\+/, name: 'box' },           // +---+ 格式的方框（至少3个连字符）
      { pattern: /[┌└├┤┬┴┼╔╚╠╣╦╩╬]/, name: 'box-drawing' }, // 制表符
      { pattern: /[→←↑↓↔⟶⟵⇒⇐⇑⇓⇔]/, name: 'arrow' },      // 箭头符号
      { pattern: /^[|│┃]{3,}/, name: 'vertical-bar' },     // 连续竖线（至少3个）
    ];

    let inAsciiArt = false;
    let asciiArtStart = 0;
    let asciiArtLines: string[] = [];
    let patternMatchCount = 0; // 需要多个模式匹配才确认

    this.lines.forEach((line, index) => {
      // 必须匹配多个模式才算 ASCII 艺术
      const matchedPatterns = asciiPatterns.filter(p => p.pattern.test(line));
      const hasMultiplePatterns = matchedPatterns.length >= 2;
      const hasBoxDrawing = matchedPatterns.some(p => p.name === 'box-drawing' || p.name === 'box');
      const isCodeBlock = this.isInCodeBlock(index);

      // 判定为 ASCII 艺术的条件：
      // 1. 匹配多个模式，或
      // 2. 包含制表符/方框符号
      const isAsciiArt = (hasMultiplePatterns || hasBoxDrawing) && !isCodeBlock;

      if (isAsciiArt) {
        if (!inAsciiArt) {
          inAsciiArt = true;
          asciiArtStart = index + 1;
          asciiArtLines = [line];
          patternMatchCount = matchedPatterns.length;
        } else {
          asciiArtLines.push(line);
          patternMatchCount += matchedPatterns.length;
        }
      } else if (inAsciiArt && line.trim() === '') {
        // 只有当连续多行都有模式匹配时才报告
        if (asciiArtLines.length >= 2 && patternMatchCount >= 3) {
          this.validateAsciiArt(asciiArtLines, asciiArtStart);
        }
        inAsciiArt = false;
        asciiArtLines = [];
        patternMatchCount = 0;
      }
    });

    if (inAsciiArt && asciiArtLines.length >= 2 && patternMatchCount >= 3) {
      this.validateAsciiArt(asciiArtLines, asciiArtStart);
    }
  }

  private validateAsciiArt(lines: string[], startLine: number): void {
    if (lines.length < 2) return;

    // 检查是否是真正的 ASCII 艺术（而不是普通文本）
    const hasBoxDrawing = lines.some(l => /[┌└├┤┬┴┼╔╚╠╣╦╩╬│─┃]/.test(l));
    const hasMultipleBoxes = lines.filter(l => /\+[-]{2,}\+/.test(l)).length >= 2;
    const hasArrows = lines.some(l => /[→←↑↓↔⟶⟵]/.test(l));
    
    // 只有包含真正的 ASCII 艺术特征才报告
    if (!hasBoxDrawing && !hasMultipleBoxes && !hasArrows) {
      return;
    }

    const widths = lines.map(l => l.length);
    const avgWidth = widths.reduce((a, b) => a + b, 0) / widths.length;

    // 只报告明显的对齐问题（差距超过 20 个字符）
    let hasAlignmentIssue = false;
    lines.forEach((line, index) => {
      if (Math.abs(line.length - avgWidth) > 20) {
        this.addWarning(
          startLine + index,
          'ascii-art-alignment',
          'ASCII 艺术图表可能存在对齐问题',
          '检查字符对齐是否正确'
        );
        hasAlignmentIssue = true;
      }
    });

    // 只在真正有问题时才检查方框闭合
    if (hasAlignmentIssue) {
      const boxStarts = lines.filter(l => /\+[-]+\+/.test(l) || /[┌╔]/.test(l)).length;
      const boxEnds = lines.filter(l => /[└╚]/.test(l)).length;

      if (boxStarts > boxEnds) {
        this.addWarning(
          startLine,
          'ascii-art-unclosed-box',
          'ASCII 艺术图表中存在未闭合的方框',
          '检查方框是否正确闭合'
        );
      }
    }

    this.registerDiagram('ascii-' + startLine, 'ascii', 'art', startLine, lines.join('\n'));
  }

  // ============== 实体注册 ==============

  private registerEntity(name: string, type: any, source: string, line: number): void {
    const entity = {
      name,
      type,
      source,
      file: this.filePath,
      line,
      attributes: new Map(),
      relationships: []
    };

    switch (type) {
      case 'class':
        if (!this.entityRegistry.classes.has(name)) {
          this.entityRegistry.classes.set(name, entity);
        }
        break;
      case 'actor':
        if (!this.entityRegistry.actors.has(name)) {
          this.entityRegistry.actors.set(name, entity);
        }
        break;
      case 'state':
        if (!this.entityRegistry.states.has(name)) {
          this.entityRegistry.states.set(name, entity);
        }
        break;
      case 'table':
        if (!this.entityRegistry.tables.has(name)) {
          this.entityRegistry.tables.set(name, entity);
        }
        break;
      case 'usecase':
        if (!this.entityRegistry.usecases.has(name)) {
          this.entityRegistry.usecases.set(name, entity);
        }
        break;
      case 'component':
        if (!this.entityRegistry.components.has(name)) {
          this.entityRegistry.components.set(name, entity);
        }
        break;
    }

    if (!this.entityRegistry.all.has(name)) {
      this.entityRegistry.all.set(name, []);
    }
    this.entityRegistry.all.get(name)!.push(entity);
  }

  // ============== 图表注册 ==============

  private registerDiagram(id: string, type: 'mermaid' | 'plantuml' | 'ascii', subType: string, line: number, content: string): void {
    const diagram: DiagramInfo = {
      id,
      type,
      subType,
      file: this.filePath,
      line,
      content,
      entities: [],
      references: [],
      completeness: createEmptyDiagramCompleteness()
    };

    this.diagramRegistry.byId.set(id, diagram);
    this.diagramRegistry.all.push(diagram);

    if (!this.diagramRegistry.byType.has(subType)) {
      this.diagramRegistry.byType.set(subType, []);
    }
    this.diagramRegistry.byType.get(subType)!.push(diagram);
  }

  // ============== 辅助方法 ==============

  private extractCodeBlocks(lang: string): Array<{ content: string; startLine: number }> {
    const blocks: Array<{ content: string; startLine: number }> = [];
    let inBlock = false;
    let blockStart = 0;
    let blockContent: string[] = [];

    this.lines.forEach((line, index) => {
      const langMatch = line.match(new RegExp(`^[\`~]{3,}${lang}`, 'i'));

      if (langMatch && !inBlock) {
        inBlock = true;
        blockStart = index + 1;
        blockContent = [];
        return;
      }

      if (inBlock) {
        if (line.match(/^[`~]{3,}$/)) {
          blocks.push({ content: blockContent.join('\n'), startLine: blockStart });
          this.registerDiagram(
            `diagram-${blockStart}`,
            lang === 'mermaid' ? 'mermaid' : 'plantuml',
            this.detectDiagramSubType(blockContent.join('\n')),
            blockStart,
            blockContent.join('\n')
          );
          inBlock = false;
        } else {
          blockContent.push(line);
        }
      }
    });

    return blocks;
  }

  private detectDiagramSubType(content: string): string {
    const patterns: [RegExp, string][] = [
      [/graph|flowchart/i, 'flowchart'],
      [/sequenceDiagram/i, 'sequence'],
      [/classDiagram/i, 'class'],
      [/stateDiagram/i, 'state'],
      [/erDiagram/i, 'er'],
      [/gantt/i, 'gantt'],
      [/pie/i, 'pie'],
      [/mindmap/i, 'mindmap'],
      [/usecase/i, 'usecase'],
    ];

    for (const [pattern, type] of patterns) {
      if (pattern.test(content)) {
        return type;
      }
    }

    return 'unknown';
  }
}
