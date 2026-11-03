#!/usr/bin/env npx ts-node
/**
 * 文档追溯性校验脚本
 * 
 * 用途：校验文档之间的追溯关系是否完整
 * 输入：文档目录路径
 * 输出：JSON 格式的校验结果
 * 
 * 用法：npx ts-node scripts/validate-traceability.ts <directory>
 */

import * as fs from 'fs';
import * as path from 'path';

// ============== 类型定义 ==============

interface TraceabilityIssue {
  severity: 'error' | 'warning' | 'info';
  code: string;
  message: string;
  documentId?: string;
  file?: string;
}

interface TraceRelation {
  sourceId: string;
  targetId: string;
  relationType: string;
  mandatory: boolean;
}

interface TraceabilityResult {
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

interface ScriptResult<T> {
  success: boolean;
  data: T;
  issues: { severity: string; code: string; message: string }[];
  suggestions: string[];
}

interface DocumentInfo {
  path: string;
  type: string;
  name: string;
}

// ============== 主函数 ==============

function validateTraceability(directory: string): ScriptResult<TraceabilityResult> {
  if (!fs.existsSync(directory)) {
    return {
      success: false,
      data: {} as TraceabilityResult,
      issues: [{ severity: 'error', code: 'DIR_NOT_FOUND', message: `目录不存在: ${directory}` }],
      suggestions: []
    };
  }

  const documents = collectDocuments(directory);
  const issues: TraceabilityIssue[] = [];
  const traceRelations: TraceRelation[] = [];

  // 收集所有 ID
  const allIds = new Map<string, { type: string; file: string }>();
  
  for (const doc of documents) {
    const content = fs.readFileSync(doc.path, 'utf-8');
    const docId = extractDocumentId(content, doc.path);
    
    if (docId) {
      allIds.set(docId, { type: doc.type, file: doc.path });
    }
  }

  // 校验每个文档的追溯关系
  for (const doc of documents) {
    const content = fs.readFileSync(doc.path, 'utf-8');
    const docIssues = validateDocumentTraceability(content, doc, allIds);
    issues.push(...docIssues);
    
    // 提取追溯关系
    const relations = extractTraceRelations(content, doc);
    traceRelations.push(...relations);
  }

  // 计算覆盖率
  const coverage = calculateCoverage(documents, traceRelations);

  // 添加覆盖率警告
  if (coverage.scenarioToUseCase < 100) {
    issues.push({
      severity: 'warning',
      code: 'COVERAGE_SC_UC',
      message: `场景到用例的覆盖率: ${coverage.scenarioToUseCase.toFixed(1)}%`
    });
  }

  if (coverage.useCaseToRequirement < 100) {
    issues.push({
      severity: 'warning',
      code: 'COVERAGE_UC_REQ',
      message: `用例到需求的覆盖率: ${coverage.useCaseToRequirement.toFixed(1)}%`
    });
  }

  if (coverage.requirementToTest < 100) {
    issues.push({
      severity: 'warning',
      code: 'COVERAGE_REQ_TC',
      message: `需求到测试的覆盖率: ${coverage.requirementToTest.toFixed(1)}%`
    });
  }

  return {
    success: issues.filter(i => i.severity === 'error').length === 0,
    data: {
      success: issues.filter(i => i.severity === 'error').length === 0,
      totalDocuments: documents.length,
      traceRelations,
      issues,
      coverage
    },
    issues: issues.map(i => ({
      severity: i.severity,
      code: i.code,
      message: i.message
    })),
    suggestions: generateSuggestions(issues)
  };
}

// ============== 文档收集 ==============

function collectDocuments(directory: string): DocumentInfo[] {
  const documents: DocumentInfo[] = [];
  
  const walk = (dir: string) => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
          walk(fullPath);
        }
      } else if (entry.isFile() && /\.md$/i.test(entry.name)) {
        documents.push({
          path: fullPath,
          type: getDocumentTypeFromPath(fullPath),
          name: entry.name
        });
      }
    }
  };

  walk(directory);
  return documents;
}

function getDocumentTypeFromPath(filePath: string): string {
  const name = path.basename(filePath).toLowerCase();
  
  if (name.includes('scenario') || name.match(/sc-\d+/)) return 'scenario';
  if (name.includes('use-case') || name.match(/uc-\d+/)) return 'use-case';
  if (name.includes('requirement') || name.match(/req-\d+/)) return 'requirement';
  if (name.includes('test') || name.match(/tc-\d+/)) return 'test';
  if (name.includes('acceptance') || name.match(/acc-\d+/)) return 'acceptance';
  if (name.includes('observability') || name.match(/obs-\d+/)) return 'observability';
  
  return 'unknown';
}

// ============== ID 提取 ==============

function extractDocumentId(content: string, filePath: string): string | null {
  const patterns = [
    /\*\*场景ID\*\*[：:]\s*(SC-\d{3,})/i,
    /\*\*用例ID\*\*[：:]\s*(UC-\d{3,})/i,
    /\*\*需求ID\*\*[：:]\s*(REQ-\d{3,})/i,
    /\*\*测试ID\*\*[：:]\s*(TC-\d{3,})/i,
    /\*\*验收ID\*\*[：:]\s*(ACC-\d{3,})/i,
    /\*\*观测ID\*\*[：:]\s*(OBS-\d{3,})/i
  ];

  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match) {
      return match[1].toUpperCase();
    }
  }

  return null;
}

// ============== 追溯校验 ==============

function validateDocumentTraceability(
  content: string,
  doc: DocumentInfo,
  allIds: Map<string, { type: string; file: string }>
): TraceabilityIssue[] {
  const issues: TraceabilityIssue[] = [];
  const docType = doc.type;

  switch (docType) {
    case 'use-case':
      if (!content.includes('来源场景') && !content.match(/SC-\d+/)) {
        issues.push({
          severity: 'error',
          code: 'SC-TR-001',
          message: `用例文档 ${doc.name} 缺少场景追溯`,
          documentId: extractDocumentId(content, doc.path) || undefined,
          file: doc.path
        });
      }
      break;

    case 'requirement':
      if (!content.includes('来源用例') && !content.match(/UC-\d+/)) {
        issues.push({
          severity: 'error',
          code: 'UC-TR-001',
          message: `需求文档 ${doc.name} 缺少用例追溯`,
          file: doc.path
        });
      }
      if (!content.match(/TC-\d+/) && !content.includes('测试')) {
        issues.push({
          severity: 'warning',
          code: 'REQ-TR-001',
          message: `需求文档 ${doc.name} 缺少测试用例关联`,
          file: doc.path
        });
      }
      break;

    case 'test':
      if (!content.includes('来源需求') && !content.match(/REQ-\d+/)) {
        issues.push({
          severity: 'warning',
          code: 'TC-TR-001',
          message: `测试文档 ${doc.name} 缺少需求追溯`,
          file: doc.path
        });
      }
      break;

    case 'acceptance':
      if (!content.includes('关联需求') && !content.match(/REQ-\d+/)) {
        issues.push({
          severity: 'warning',
          code: 'ACC-TR-001',
          message: `验收文档 ${doc.name} 缺少需求追溯`,
          file: doc.path
        });
      }
      break;
  }

  return issues;
}

// ============== 关系提取 ==============

function extractTraceRelations(content: string, doc: DocumentInfo): TraceRelation[] {
  const relations: TraceRelation[] = [];
  const docId = extractDocumentId(content, doc.path);
  
  if (!docId) return relations;

  // 匹配 **来源场景**: SC-XXX 或 来源场景: SC-XXX
  const scenarioMatch = content.match(/来源场景[^\n]*?(SC-\d{3,})/i);
  if (scenarioMatch) {
    relations.push({
      sourceId: docId,
      targetId: scenarioMatch[1].toUpperCase(),
      relationType: 'derives',
      mandatory: true
    });
  }

  // 匹配 **来源用例**: UC-XXX 或 来源用例: UC-XXX
  const useCaseMatch = content.match(/来源用例[^\n]*?(UC-\d{3,})/i);
  if (useCaseMatch) {
    relations.push({
      sourceId: docId,
      targetId: useCaseMatch[1].toUpperCase(),
      relationType: 'requires',
      mandatory: true
    });
  }

  // 匹配 **关联需求**: REQ-XXX 或 **来源需求**: REQ-XXX
  const requirementMatch = content.match(/(关联需求|来源需求)[^\n]*?(REQ-\d{3,})/i);
  if (requirementMatch) {
    relations.push({
      sourceId: docId,
      targetId: requirementMatch[2].toUpperCase(),
      relationType: 'verifies',
      mandatory: true
    });
  }

  return relations;
}

// ============== 覆盖率计算 ==============

function calculateCoverage(
  documents: DocumentInfo[],
  relations: TraceRelation[]
): TraceabilityResult['coverage'] {
  const counts = {
    scenario: 0,
    useCase: 0,
    requirement: 0,
    test: 0,
    acceptance: 0
  };

  for (const doc of documents) {
    const type = doc.type;
    if (type in counts) {
      counts[type as keyof typeof counts]++;
    }
  }

  const tracedCounts = {
    scenarioToUseCase: new Set<string>(),
    useCaseToRequirement: new Set<string>()
  };

  for (const rel of relations) {
    if (rel.relationType === 'derives') {
      tracedCounts.scenarioToUseCase.add(rel.targetId);
    }
    if (rel.relationType === 'requires') {
      tracedCounts.useCaseToRequirement.add(rel.targetId);
    }
  }

  return {
    scenarioToUseCase: counts.scenario > 0 
      ? (tracedCounts.scenarioToUseCase.size / counts.scenario) * 100 
      : 100,
    useCaseToRequirement: counts.useCase > 0 
      ? (tracedCounts.useCaseToRequirement.size / counts.useCase) * 100 
      : 100,
    requirementToTest: counts.requirement > 0 
      ? Math.min(100, (counts.test / counts.requirement) * 100) 
      : 100,
    requirementToAcceptance: counts.requirement > 0 
      ? Math.min(100, (counts.acceptance / counts.requirement) * 100) 
      : 100
  };
}

// ============== 建议生成 ==============

function generateSuggestions(issues: TraceabilityIssue[]): string[] {
  const suggestions: string[] = [];

  const errorCount = issues.filter(i => i.severity === 'error').length;
  if (errorCount > 0) {
    suggestions.push(`发现 ${errorCount} 个严重问题，请优先修复`);
  }

  const issueTypes = new Set(issues.map(i => i.code));

  if (issueTypes.has('SC-TR-001')) {
    suggestions.push('为每个用例添加场景追溯（来源场景: SC-XXX）');
  }
  if (issueTypes.has('UC-TR-001')) {
    suggestions.push('为每个需求添加用例追溯（来源用例: UC-XXX）');
  }
  if (issueTypes.has('REQ-TR-001')) {
    suggestions.push('为每个需求添加至少一个测试用例');
  }

  return suggestions;
}

// ============== CLI 入口 ==============

function main(): void {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('用法: npx ts-node scripts/validate-traceability.ts <directory>');
    console.error('');
    console.error('校验文档追溯关系完整性，输出覆盖率报告。');
    process.exit(1);
  }

  const directory = args[0];
  const result = validateTraceability(directory);
  
  console.log(JSON.stringify(result, null, 2));
}

// 执行入口
main();

export { validateTraceability };
