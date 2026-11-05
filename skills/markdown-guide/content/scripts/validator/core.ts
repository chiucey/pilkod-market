/**
 * Markdown 校验器核心模块
 * 
 * 包含所有类型定义、基础类和工具函数
 */

// ============== 类型定义 ==============

export interface ValidationError {
  file?: string;
  line: number;
  column?: number;
  type: 'error' | 'warning' | 'info';
  rule: string;
  message: string;
  suggestion?: string;
  context?: string;
}

export interface ValidationResult {
  file: string;
  documentType: DocumentType;
  errors: ValidationError[];
  warnings: ValidationError[];
  info: ValidationError[];
  summary: {
    total: number;
    errors: number;
    warnings: number;
    info: number;
  };
  entities: EntityRegistry;
  diagrams: DiagramRegistry;
  codeBlocks: CodeBlockInfo[];
  crossFileRefs: CrossFileReference[];
  documentStandards: DocumentStandardResult;
}

export interface HeadingInfo {
  level: number;
  text: string;
  line: number;
  id: string;
}

export interface TocEntry {
  text: string;
  level: number;
  id: string;
}

export interface EntityDefinition {
  name: string;
  type: 'class' | 'table' | 'state' | 'actor' | 'component' | 'usecase' | 'custom';
  source: string;
  file: string;
  line: number;
  attributes?: Map<string, string>;
  relationships?: string[];
}

export interface EntityRegistry {
  classes: Map<string, EntityDefinition>;
  actors: Map<string, EntityDefinition>;
  states: Map<string, EntityDefinition>;
  tables: Map<string, EntityDefinition>;
  components: Map<string, EntityDefinition>;
  usecases: Map<string, EntityDefinition>;
  all: Map<string, EntityDefinition[]>;
}

export interface DiagramInfo {
  id: string;
  type: 'mermaid' | 'plantuml' | 'ascii';
  subType: string;
  file: string;
  line: number;
  content: string;
  entities: string[];
  references: string[];
  completeness: DiagramCompleteness;
}

export interface DiagramCompleteness {
  hasStart: boolean;
  hasEnd: boolean;
  hasBranches: boolean;
  branchesComplete: boolean;
  allNodesReachable: boolean;
  participantCount: number;
  messageCount: number;
  actorCount: number;
  usecaseCount: number;
}

export interface DiagramRegistry {
  byId: Map<string, DiagramInfo>;
  byType: Map<string, DiagramInfo[]>;
  all: DiagramInfo[];
}

export interface CodeBlockInfo {
  line: number;
  language: string;
  content: string;
  hasLanguageTag: boolean;
  spellingErrors: SpellingError[];
  syntaxErrors: SyntaxError[];
  nestedMarkdown: boolean;
}

export interface SpellingError {
  word: string;
  line: number;
  column: number;
  suggestions: string[];
}

export interface SyntaxError {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning';
}

export interface CrossFileReference {
  sourceFile: string;
  targetFile: string;
  sourceLine: number;
  refType: 'link' | 'image' | 'include';
  valid: boolean;
}

export interface CrossFileValidationResult {
  files: string[];
  errors: ValidationError[];
  warnings: ValidationError[];
  entityConsistency: EntityConsistencyIssue[];
  logicConsistency: LogicConsistencyIssue[];
}

export interface EntityConsistencyIssue {
  entityName: string;
  files: string[];
  issue: string;
  severity: 'error' | 'warning';
}

export interface LogicConsistencyIssue {
  type: 'state-mismatch' | 'flow-mismatch' | 'relationship-mismatch';
  files: string[];
  description: string;
}

// ============== 文档类型定义 ==============

export type DocumentType = 
  | 'readme'
  | 'api-documentation'
  | 'technical-guide'
  | 'faq'
  | 'changelog'
  | 'contributing'
  | 'design-doc'
  | 'workflow-doc'
  | 'specification'
  | 'man-page'
  | 'user-documentation'
  | 'quickstart'
  | 'blog-post'
  | 'tutorial'
  | 'reference'
  | 'unknown';

export interface DocumentTypePattern {
  type: DocumentType;
  patterns: RegExp[];
  requiredSections: string[];
  optionalSections: string[];
  priority: number;
}

export interface DocumentStandardResult {
  detectedType: DocumentType;
  confidence: number;
  standardChecks: StandardCheck[];
  overallScore: number;
  missingSections: string[];
  suggestedSections: string[];
}

export interface StandardCheck {
  rule: string;
  passed: boolean;
  message: string;
  importance: 'required' | 'recommended' | 'optional';
}

// ============== 校验器基类 ==============

export abstract class BaseValidator {
  protected errors: ValidationError[] = [];
  protected warnings: ValidationError[] = [];
  protected info: ValidationError[] = [];
  protected lines: string[];
  protected content: string;
  protected filePath: string;

  constructor(content: string, filePath: string) {
    this.content = content;
    this.lines = content.split('\n');
    this.filePath = filePath;
  }

  protected addError(line: number, rule: string, message: string, suggestion?: string): void {
    this.errors.push({ line, type: 'error', rule, message, suggestion });
  }

  protected addWarning(line: number, rule: string, message: string, suggestion?: string): void {
    this.warnings.push({ line, type: 'warning', rule, message, suggestion });
  }

  protected addInfo(line: number, rule: string, message: string, suggestion?: string): void {
    this.info.push({ line, type: 'info', rule, message, suggestion });
  }

  protected isInCodeBlock(lineIndex: number): boolean {
    let codeBlockCount = 0;
    for (let i = 0; i < lineIndex; i++) {
      if (this.lines[i].match(/^```/)) {
        codeBlockCount++;
      }
    }
    return codeBlockCount % 2 === 1;
  }

  protected generateHeadingId(text: string): string {
    return text
      .toLowerCase()
      .replace(/[^\w\u4e00-\u9fa5]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  abstract validate(): void;

  getResults(): { errors: ValidationError[]; warnings: ValidationError[]; info: ValidationError[] } {
    return {
      errors: this.errors,
      warnings: this.warnings,
      info: this.info
    };
  }
}

// ============== 工具函数 ==============

export function createEmptyEntityRegistry(): EntityRegistry {
  return {
    classes: new Map(),
    actors: new Map(),
    states: new Map(),
    tables: new Map(),
    components: new Map(),
    usecases: new Map(),
    all: new Map()
  };
}

export function createEmptyDiagramRegistry(): DiagramRegistry {
  return {
    byId: new Map(),
    byType: new Map(),
    all: []
  };
}

export function createEmptyDiagramCompleteness(): DiagramCompleteness {
  return {
    hasStart: false,
    hasEnd: false,
    hasBranches: false,
    branchesComplete: true,
    allNodesReachable: true,
    participantCount: 0,
    messageCount: 0,
    actorCount: 0,
    usecaseCount: 0
  };
}

export function mergeValidationResults(
  ...results: { errors: ValidationError[]; warnings: ValidationError[]; info: ValidationError[] }[]
): { errors: ValidationError[]; warnings: ValidationError[]; info: ValidationError[] } {
  const merged = { errors: [], warnings: [], info: [] } as any;
  
  results.forEach(r => {
    merged.errors.push(...r.errors);
    merged.warnings.push(...r.warnings);
    merged.info.push(...r.info);
  });
  
  return merged;
}
