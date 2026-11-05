/**
 * Harness 工程文档引擎 - 核心类型定义
 */

// ============== 文档 ID 类型 ==============

export type DocumentType = 
  | 'scenario'      // 场景
  | 'use-case'      // 用例
  | 'requirement'   // 需求
  | 'test'          // 测试
  | 'acceptance'    // 验收
  | 'observability' // 观测
  | 'code';         // 代码

export type IdPrefix = 'SC' | 'UC' | 'REQ' | 'TC' | 'AC' | 'ACC' | 'OBS' | 'ALT' | 'BR' | 'ISS' | 'BUG';

export interface DocumentId {
  prefix: IdPrefix;
  number: number;
  subNumber?: number;  // 用于 AC-NNN-M 格式
  toString(): string;
}

// ============== 追溯关系 ==============

export interface TraceRelation {
  sourceId: string;
  targetId: string;
  relationType: 'derives' | 'requires' | 'verified-by' | 'satisfied-by' | 'tested-by' | 'measured-by' | 'traces-to';
  mandatory: boolean;
}

export interface TraceabilityResult {
  success: boolean;
  totalDocuments: number;
  traceRelations: TraceRelation[];
  issues: TraceabilityIssue[];
  coverage: {
    scenarioToUseCase: number;
    useCaseToRequirement: number;
    requirementToTest: number;
    requirementToAcceptance: number;
  };
}

export interface TraceabilityIssue {
  severity: 'error' | 'warning' | 'info';
  code: string;
  message: string;
  documentId?: string;
  file?: string;
}

// ============== 覆盖率结果 ==============

export interface CoverageResult {
  success: boolean;
  requirementCoverage: number;
  testCoverage: number;
  acceptanceCoverage: number;
  codeCoverage: number;
  uncoveredRequirements: string[];
  uncoveredTests: string[];
  uncoveredAcceptance: string[];
}

// ============== 校验结果 ==============

export interface ValidationResult {
  success: boolean;
  documentType: DocumentType;
  documentId: string;
  issues: ValidationIssue[];
  suggestions: string[];
}

export interface ValidationIssue {
  severity: 'error' | 'warning' | 'info';
  code: string;
  message: string;
  line?: number;
  field?: string;
}

// ============== 脚本统一输出格式 ==============

export interface ScriptResult<T> {
  success: boolean;
  data: T;
  issues: Issue[];
  suggestions: string[];
}

export interface Issue {
  severity: 'error' | 'warning' | 'info';
  code: string;
  message: string;
  line?: number;
  file?: string;
}

// ============== 追溯矩阵 ==============

export interface TraceMatrix {
  requirements: string[];
  testCases: string[];
  acceptanceCriteria: string[];
  relations: {
    requirement: string;
    tests: string[];
    acceptance: string[];
  }[];
  coverage: {
    requirementTestCoverage: number;
    requirementAcceptanceCoverage: number;
  };
}

// ============== 生命周期状态 ==============

export type LifecycleStage = 
  | 'scenario'
  | 'use-case'
  | 'requirement'
  | 'code'
  | 'test'
  | 'acceptance'
  | 'deploy'
  | 'observability'
  | 'iteration';

export type LifecycleStatus = 
  | 'draft'
  | 'review'
  | 'approved'
  | 'implemented'
  | 'tested'
  | 'accepted'
  | 'deployed'
  | 'active'
  | 'deprecated';

export interface LifecycleState {
  stage: LifecycleStage;
  status: LifecycleStatus;
  transitions: LifecycleTransition[];
}

export interface LifecycleTransition {
  from: LifecycleStage;
  to: LifecycleStage;
  trigger: string;
  qualityGate: string[];
}

// ============== 辅助函数 ==============

export function createSuccessResult<T>(data: T, suggestions: string[] = []): ScriptResult<T> {
  return {
    success: true,
    data,
    issues: [],
    suggestions
  };
}

export function createErrorResult<T>(message: string, code: string): ScriptResult<T> {
  return {
    success: false,
    data: {} as T,
    issues: [{ severity: 'error', code, message }],
    suggestions: []
  };
}

export function parseDocumentId(id: string): DocumentId | null {
  const match = id.match(/^(SC|UC|REQ|TC|AC|ACC|OBS|ALT|BR|ISS|BUG)-(\d{3,})(?:-(\d+))?$/i);
  if (!match) return null;
  
  return {
    prefix: match[1].toUpperCase() as IdPrefix,
    number: parseInt(match[2], 10),
    subNumber: match[3] ? parseInt(match[3], 10) : undefined,
    toString: () => id.toUpperCase()
  };
}

export function isValidDocumentId(id: string): boolean {
  return parseDocumentId(id) !== null;
}

export function getDocumentType(id: string): DocumentType | null {
  const parsed = parseDocumentId(id);
  if (!parsed) return null;
  
  const typeMap: Record<IdPrefix, DocumentType> = {
    'SC': 'scenario',
    'UC': 'use-case',
    'REQ': 'requirement',
    'TC': 'test',
    'AC': 'acceptance',
    'ACC': 'acceptance',
    'OBS': 'observability',
    'ALT': 'observability',
    'BR': 'requirement',
    'ISS': 'acceptance',
    'BUG': 'test'
  };
  
  return typeMap[parsed.prefix] || null;
}
