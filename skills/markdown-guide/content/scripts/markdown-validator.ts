/**
 * Markdown 文档校验器主入口
 * 
 * 整合所有校验模块，提供统一的校验入口
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  ValidationResult,
  ValidationError,
  EntityRegistry,
  DiagramRegistry,
  CodeBlockInfo,
  CrossFileReference,
  DocumentStandardResult,
  createEmptyEntityRegistry,
  createEmptyDiagramRegistry
} from './validator/core';
import { BasicValidator } from './validator/basic';
import { CodeValidator } from './validator/code';
import { DiagramValidator } from './validator/diagram';
import { WorkflowValidator } from './validator/workflow';
import { EntityValidator } from './validator/entity';
import { CrossFileValidator } from './validator/cross-file';
import { DocumentTypeValidator } from './validator/document-type';

export interface ValidatorOptions {
  enableSpellingCheck?: boolean;
  enableSyntaxCheck?: boolean;
  enableCrossFileCheck?: boolean;
  enableDocumentTypeCheck?: boolean;
}

export class MarkdownValidator {
  private options: ValidatorOptions;

  constructor(options: ValidatorOptions = {}) {
    this.options = {
      enableSpellingCheck: true,
      enableSyntaxCheck: true,
      enableCrossFileCheck: false,
      enableDocumentTypeCheck: true,
      ...options
    };
  }

  validateFile(filePath: string): ValidationResult {
    let content = fs.readFileSync(filePath, 'utf-8');
    // 统一换行符为 LF
    content = content.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    return this.validateContent(content, filePath);
  }

  validateContent(content: string, filePath: string): ValidationResult {
    // 确保 content 使用统一换行符
    content = content.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const errors: ValidationError[] = [];
    const warnings: ValidationError[] = [];
    const info: ValidationError[] = [];

    let entityRegistry = createEmptyEntityRegistry();
    let diagramRegistry = createEmptyDiagramRegistry();
    let codeBlocks: CodeBlockInfo[] = [];
    let crossFileRefs: CrossFileReference[] = [];
    let documentStandards: DocumentStandardResult = {
      detectedType: 'unknown',
      confidence: 0,
      standardChecks: [],
      overallScore: 0,
      missingSections: [],
      suggestedSections: []
    };

    // 1. 基础校验
    const basicValidator = new BasicValidator(content, filePath);
    basicValidator.validate();
    const basicResults = basicValidator.getResults();
    errors.push(...basicResults.errors);
    warnings.push(...basicResults.warnings);
    info.push(...basicResults.info);

    // 2. 代码块校验
    const codeValidator = new CodeValidator(content, filePath);
    codeValidator.validate();
    const codeResults = codeValidator.getResults();
    errors.push(...codeResults.errors);
    warnings.push(...codeResults.warnings);
    info.push(...codeResults.info);
    codeBlocks = codeValidator.getCodeBlocks();

    // 3. 图表校验
    const diagramValidator = new DiagramValidator(content, filePath, entityRegistry);
    diagramValidator.validate();
    const diagramResults = diagramValidator.getResults();
    errors.push(...diagramResults.errors);
    warnings.push(...diagramResults.warnings);
    info.push(...diagramResults.info);
    entityRegistry = diagramValidator.getEntityRegistry() as EntityRegistry;
    diagramRegistry = diagramValidator.getDiagramRegistry();

    // 4. 工作流完整性校验
    const workflowValidator = new WorkflowValidator(diagramRegistry);
    const workflowResults = workflowValidator.validate();
    warnings.push(...workflowResults.warnings);
    info.push(...workflowResults.info);

    // 5. 实体一致性校验
    const entityValidator = new EntityValidator(entityRegistry, diagramRegistry, filePath);
    const entityResults = entityValidator.validate();
    warnings.push(...entityResults.warnings);

    // 6. 文档类型识别与标准校验
    if (this.options.enableDocumentTypeCheck) {
      const docTypeValidator = new DocumentTypeValidator(content, filePath);
      docTypeValidator.validate();
      const docTypeResults = docTypeValidator.getResults();
      errors.push(...docTypeResults.errors);
      warnings.push(...docTypeResults.warnings);
      info.push(...docTypeResults.info);
      documentStandards = docTypeValidator.getResult();
    }

    const total = errors.length + warnings.length + info.length;

    return {
      file: filePath,
      documentType: documentStandards.detectedType,
      errors,
      warnings,
      info,
      summary: { total, errors: errors.length, warnings: warnings.length, info: info.length },
      entities: entityRegistry,
      diagrams: diagramRegistry,
      codeBlocks,
      crossFileRefs,
      documentStandards
    };
  }

  validateFiles(files: string[]): ValidationResult[] {
    return files.map(file => this.validateFile(file));
  }

  validateDirectory(dirPath: string): ValidationResult[] {
    const files = this.collectMarkdownFiles(dirPath);
    return this.validateFiles(files);
  }

  private collectMarkdownFiles(dirPath: string): string[] {
    const files: string[] = [];

    const walk = (dir: string) => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      entries.forEach((entry: fs.Dirent) => {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
            walk(fullPath);
          }
        } else if (entry.isFile() && /\.md$/i.test(entry.name)) {
          files.push(fullPath);
        }
      });
    };

    walk(dirPath);
    return files;
  }
}

// ============== 命令行入口 ==============

function printResult(result: ValidationResult): void {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`文件: ${result.file}`);
  console.log(`文档类型: ${result.documentType}`);
  console.log(`评分: ${result.documentStandards.overallScore.toFixed(1)}%`);
  console.log(`${'='.repeat(60)}`);

  if (result.errors.length > 0) {
    console.log(`\n❌ 错误 (${result.errors.length}):`);
    result.errors.forEach(e => {
      console.log(`  [L${e.line}] ${e.message}`);
      if (e.suggestion) console.log(`    建议: ${e.suggestion}`);
    });
  }

  if (result.warnings.length > 0) {
    console.log(`\n⚠️  警告 (${result.warnings.length}):`);
    result.warnings.forEach(w => {
      console.log(`  [L${w.line}] ${w.message}`);
      if (w.suggestion) console.log(`    建议: ${w.suggestion}`);
    });
  }

  if (result.info.length > 0) {
    console.log(`\nℹ️  提示 (${result.info.length}):`);
    result.info.slice(0, 5).forEach(i => {
      console.log(`  [L${i.line}] ${i.message}`);
    });
    if (result.info.length > 5) {
      console.log(`  ... 还有 ${result.info.length - 5} 条提示`);
    }
  }

  console.log(`\n📊 统计:`);
  console.log(`  错误: ${result.summary.errors}`);
  console.log(`  警告: ${result.summary.warnings}`);
  console.log(`  提示: ${result.summary.info}`);
  console.log(`  总计: ${result.summary.total}`);

  if (result.documentStandards.missingSections.length > 0) {
    console.log(`\n📋 缺少章节: ${result.documentStandards.missingSections.join(', ')}`);
  }
}

function main(): void {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('用法: npx ts-node markdown-validator.ts <file-or-directory>');
    console.log('选项:');
    console.log('  --no-spell    禁用拼写检查');
    console.log('  --no-syntax   禁用语法检查');
    console.log('  --cross-file  启用跨文件检查');
    process.exit(1);
  }

  const options: ValidatorOptions = {
    enableSpellingCheck: !args.includes('--no-spell'),
    enableSyntaxCheck: !args.includes('--no-syntax'),
    enableCrossFileCheck: args.includes('--cross-file'),
    enableDocumentTypeCheck: true
  };

  const validator = new MarkdownValidator(options);
  const targetPath = args.find((a: string) => !a.startsWith('--'));

  if (!targetPath) {
    console.error('请指定文件或目录');
    process.exit(1);
  }

  try {
    const stat = fs.statSync(targetPath);

    if (stat.isDirectory()) {
      const results = validator.validateDirectory(targetPath);
      results.forEach(printResult);

      const totalErrors = results.reduce((sum, r) => sum + r.summary.errors, 0);
      const totalWarnings = results.reduce((sum, r) => sum + r.summary.warnings, 0);

      console.log(`\n${'='.repeat(60)}`);
      console.log(`总计: ${results.length} 个文件`);
      console.log(`总错误: ${totalErrors}`);
      console.log(`总警告: ${totalWarnings}`);

      process.exit(totalErrors > 0 ? 1 : 0);
    } else {
      const result = validator.validateFile(targetPath);
      printResult(result);
      process.exit(result.summary.errors > 0 ? 1 : 0);
    }
  } catch (error: any) {
    console.error(`错误: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export default MarkdownValidator;
