/**
 * 跨文件引用与实体一致性校验模块
 * 
 * 包含跨文件链接校验、实体定义一致性检查、全局引用关系分析
 */

import {
  EntityRegistry,
  DiagramRegistry,
  CrossFileReference,
  CrossFileValidationResult,
  EntityConsistencyIssue,
  LogicConsistencyIssue,
  ValidationError
} from './core';
import * as path from 'path';
import * as fs from 'fs';

export class CrossFileValidator {
  private errors: ValidationError[] = [];
  private warnings: ValidationError[] = [];
  private basePath: string;

  constructor(basePath: string) {
    this.basePath = basePath;
  }

  validate(files: string[]): CrossFileValidationResult {
    this.errors = [];
    this.warnings = [];

    const crossFileRefs: CrossFileReference[] = [];
    const entityConsistency: EntityConsistencyIssue[] = [];
    const logicConsistency: LogicConsistencyIssue[] = [];

    files.forEach(file => {
      const refs = this.extractCrossFileReferences(file);
      crossFileRefs.push(...refs);
    });

    const entityRegistry = this.buildGlobalEntityRegistry(files);
    entityConsistency.push(...this.checkEntityConsistency(entityRegistry));

    logicConsistency.push(...this.checkLogicConsistency(files));

    return {
      files,
      errors: this.errors,
      warnings: this.warnings,
      entityConsistency,
      logicConsistency
    };
  }

  // ============== 跨文件引用提取 ==============

  private extractCrossFileReferences(filePath: string): CrossFileReference[] {
    const refs: CrossFileReference[] = [];

    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const lines = content.split('\n');
      const dir = path.dirname(filePath);

      lines.forEach((line: string, index: number) => {
        const linkPattern = /\[([^\]]*)\]\(([^)#)]+)(?:#([^)]*))?\)/g;
        let match;

        while ((match = linkPattern.exec(line)) !== null) {
          const targetPath = match[2];
          const fragment = match[3];

          if (targetPath.startsWith('http://') || targetPath.startsWith('https://')) {
            return;
          }

          if (targetPath.startsWith('mailto:') || targetPath.startsWith('#')) {
            return;
          }

          const fullPath = this.resolvePath(dir, targetPath);
          const isValid = this.checkFileExists(fullPath);

          refs.push({
            sourceFile: filePath,
            targetFile: fullPath,
            sourceLine: index + 1,
            refType: 'link',
            valid: isValid
          });

          if (!isValid) {
            this.errors.push({
              file: filePath,
              line: index + 1,
              type: 'error',
              rule: 'cross-file-broken-link',
              message: `跨文件链接指向不存在的文件: ${targetPath}`,
              suggestion: '检查文件路径是否正确，或创建目标文件'
            });
          }
        }

        const imgPattern = /!\[([^\]]*)\]\(([^)]+)\)/g;
        while ((match = imgPattern.exec(line)) !== null) {
          const targetPath = match[2];

          if (targetPath.startsWith('http://') || targetPath.startsWith('https://')) {
            return;
          }

          const fullPath = this.resolvePath(dir, targetPath);
          const isValid = this.checkFileExists(fullPath);

          refs.push({
            sourceFile: filePath,
            targetFile: fullPath,
            sourceLine: index + 1,
            refType: 'image',
            valid: isValid
          });

          if (!isValid) {
            this.warnings.push({
              file: filePath,
              line: index + 1,
              type: 'warning',
              rule: 'cross-file-broken-image',
              message: `图片文件不存在: ${targetPath}`,
              suggestion: '检查图片路径是否正确，或添加图片文件'
            });
          }
        }
      });
    } catch (error) {
      this.errors.push({
        file: filePath,
        line: 0,
        type: 'error',
        rule: 'file-read-error',
        message: `无法读取文件: ${filePath}`,
        suggestion: '检查文件是否存在且可读'
      });
    }

    return refs;
  }

  private resolvePath(baseDir: string, relativePath: string): string {
    if (path.isAbsolute(relativePath)) {
      return relativePath;
    }
    return path.resolve(baseDir, relativePath);
  }

  private checkFileExists(filePath: string): boolean {
    try {
      return fs.existsSync(filePath);
    } catch {
      return false;
    }
  }

  // ============== 全局实体注册表构建 ==============

  private buildGlobalEntityRegistry(files: string[]): Map<string, any[]> {
    const globalRegistry = new Map<string, any[]>();

    files.forEach(file => {
      try {
        const content = fs.readFileSync(file, 'utf-8');

        const classPattern = /class\s+(\w+)/g;
        let match;
        while ((match = classPattern.exec(content)) !== null) {
          const className = match[1];
          if (!globalRegistry.has(className)) {
            globalRegistry.set(className, []);
          }
          globalRegistry.get(className)!.push({
            name: className,
            type: 'class',
            file: file,
            line: content.substring(0, match.index).split('\n').length
          });
        }

        const entityPattern = /entity\s+"?(\w+)"?/gi;
        while ((match = entityPattern.exec(content)) !== null) {
          const entityName = match[1];
          if (!globalRegistry.has(entityName)) {
            globalRegistry.set(entityName, []);
          }
          globalRegistry.get(entityName)!.push({
            name: entityName,
            type: 'entity',
            file: file,
            line: content.substring(0, match.index).split('\n').length
          });
        }

        const headingPattern = /^#{1,6}\s+(.+)$/gm;
        while ((match = headingPattern.exec(content)) !== null) {
          const heading = match[1].trim();
          const headingId = heading
            .toLowerCase()
            .replace(/[^\w\u4e00-\u9fa5]+/g, '-')
            .replace(/^-+|-+$/g, '');

          if (!globalRegistry.has(headingId)) {
            globalRegistry.set(headingId, []);
          }
          globalRegistry.get(headingId)!.push({
            name: heading,
            type: 'heading',
            file: file,
            line: content.substring(0, match.index).split('\n').length
          });
        }
      } catch (error) {
        // 忽略读取错误，已在提取引用时处理
      }
    });

    return globalRegistry;
  }

  // ============== 实体一致性检查 ==============

  private checkEntityConsistency(globalRegistry: Map<string, any[]>): EntityConsistencyIssue[] {
    const issues: EntityConsistencyIssue[] = [];

    globalRegistry.forEach((definitions, name) => {
      if (definitions.length > 1) {
        const files = definitions.map(d => d.file);
        const types = new Set(definitions.map(d => d.type));

        if (types.size > 1) {
          issues.push({
            entityName: name,
            files: files,
            issue: `实体 "${name}" 在不同文件中被定义为不同类型`,
            severity: 'warning'
          });

          this.warnings.push({
            line: 1,
            type: 'warning',
            rule: 'cross-file-entity-type-mismatch',
            message: `实体 "${name}" 在多个文件中定义类型不一致`,
            suggestion: '统一实体定义，或使用不同名称区分'
          });
        }

        const uniqueFiles = new Set(files);
        if (uniqueFiles.size > 1) {
          issues.push({
            entityName: name,
            files: Array.from(uniqueFiles),
            issue: `实体 "${name}" 在多个文件中重复定义`,
            severity: 'warning'
          });
        }
      }
    });

    return issues;
  }

  // ============== 逻辑一致性检查 ==============

  private checkLogicConsistency(files: string[]): LogicConsistencyIssue[] {
    const issues: LogicConsistencyIssue[] = [];

    const stateMachines = this.extractStateMachines(files);
    const flowcharts = this.extractFlowcharts(files);

    if (stateMachines.length > 1) {
      const allStates = new Set<string>();
      stateMachines.forEach(sm => {
        sm.states.forEach(s => allStates.add(s));
      });

      stateMachines.forEach(sm => {
        sm.states.forEach(state => {
          const foundInOthers = stateMachines
            .filter(other => other !== sm)
            .some(other => other.states.includes(state));

          if (!foundInOthers && allStates.size > 1) {
            // 可以添加一致性检查逻辑
          }
        });
      });
    }

    return issues;
  }

  private extractStateMachines(files: string[]): Array<{ file: string; states: string[] }> {
    const machines: Array<{ file: string; states: string[] }> = [];

    files.forEach(file => {
      try {
        const content = fs.readFileSync(file, 'utf-8');
        const states: string[] = [];

        const statePattern = /state\s+"?([^"\n:]+)"?/gi;
        let match;
        while ((match = statePattern.exec(content)) !== null) {
          states.push(match[1]);
        }

        if (states.length > 0) {
          machines.push({ file, states });
        }
      } catch {
        // 忽略错误
      }
    });

    return machines;
  }

  private extractFlowcharts(files: string[]): Array<{ file: string; nodes: string[] }> {
    const charts: Array<{ file: string; nodes: string[] }> = [];

    files.forEach(file => {
      try {
        const content = fs.readFileSync(file, 'utf-8');
        const nodes: string[] = [];

        const nodePattern = /\[([^\]]+)\]|\(([^)]+)\)|\{([^}]+)\}/g;
        let match;
        while ((match = nodePattern.exec(content)) !== null) {
          nodes.push(match[1] || match[2] || match[3]);
        }

        if (nodes.length > 0) {
          charts.push({ file, nodes });
        }
      } catch {
        // 忽略错误
      }
    });

    return charts;
  }
}
