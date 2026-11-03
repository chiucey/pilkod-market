/**
 * 实体与逻辑一致性校验模块
 * 
 * 包含实体一致性检查、图表关系检查、逻辑表达一致性检查
 */

import { EntityRegistry, DiagramRegistry, ValidationError } from './core';

export class EntityValidator {
  private errors: ValidationError[] = [];
  private warnings: ValidationError[] = [];
  private entityRegistry: EntityRegistry;
  private diagramRegistry: DiagramRegistry;
  private filePath: string;

  constructor(entityRegistry: EntityRegistry, diagramRegistry: DiagramRegistry, filePath: string) {
    this.entityRegistry = entityRegistry;
    this.diagramRegistry = diagramRegistry;
    this.filePath = filePath;
  }

  validate(): { errors: ValidationError[]; warnings: ValidationError[] } {
    this.errors = [];
    this.warnings = [];

    this.checkEntityConsistency();
    this.checkDiagramRelationships();
    this.checkLogicalConsistency();

    return {
      errors: this.errors,
      warnings: this.warnings
    };
  }

  // ============== 实体一致性校验 ==============

  private checkEntityConsistency(): void {
    this.entityRegistry.all.forEach((entities, name) => {
      if (entities.length > 1) {
        // 检查类型一致性
        const types = new Set(entities.map(e => e.type));
        if (types.size > 1) {
          const typeList = Array.from(types).join(', ');
          this.warnings.push({
            line: entities[0].line,
            type: 'warning',
            rule: 'entity-type-inconsistent',
            message: `实体 "${name}" 在不同图表中被定义为不同类型: ${typeList}`,
            suggestion: '确认实体定义是否需要统一命名或区分'
          });
        }

        // 检查来源一致性
        const sources = new Set(entities.map(e => e.source));
        if (sources.size > 1) {
          entities.forEach(entity => {
            this.warnings.push({
              line: entity.line,
              type: 'warning',
              rule: 'entity-multiple-definitions',
              message: `实体 "${name}" 在多个图表中定义 (${entity.source})`,
              suggestion: '检查实体定义是否一致，考虑统一管理'
            });
          });
        }
      }
    });

    // 检查命名一致性
    this.entityRegistry.all.forEach((entities, name) => {
      const nameVariants = new Set<string>();
      entities.forEach(e => {
        nameVariants.add(e.name);
      });

      if (nameVariants.size > 1) {
        this.warnings.push({
          line: entities[0].line,
          type: 'warning',
          rule: 'entity-naming-inconsistent',
          message: `实体命名不一致: ${Array.from(nameVariants).join(', ')}`,
          suggestion: '统一实体命名规范'
        });
      }
    });
  }

  // ============== 图表关系校验 ==============

  private checkDiagramRelationships(): void {
    const diagramRefs: Map<string, string[]> = new Map();

    this.diagramRegistry.all.forEach(diagram => {
      const refPattern = /\[([^\]]+)\]\(#([^)]+)\)/g;
      let match;
      const refs: string[] = [];

      while ((match = refPattern.exec(diagram.content)) !== null) {
        refs.push(match[2]);
      }

      if (refs.length > 0) {
        diagramRefs.set(diagram.id, refs);
      }
    });

    diagramRefs.forEach((refs, diagramId) => {
      refs.forEach(ref => {
        if (!this.diagramRegistry.byId.has(ref)) {
          this.warnings.push({
            line: this.diagramRegistry.byId.get(diagramId)?.line || 0,
            type: 'warning',
            rule: 'diagram-broken-reference',
            message: `图表引用 #${ref} 指向的目标不存在`,
            suggestion: '检查图表 ID 是否正确'
          });
        }
      });
    });

    this.checkDiagramLogicConsistency();
  }

  private checkDiagramLogicConsistency(): void {
    const flowcharts = this.diagramRegistry.byType.get('flowchart') || [];
    const sequences = this.diagramRegistry.byType.get('sequence') || [];

    if (flowcharts.length > 0 && sequences.length > 0) {
      const flowchartNodes = new Set<string>();
      flowcharts.forEach(fc => {
        const nodePattern = /\[([^\]]+)\]|\(([^)]+)\)|\{([^}]+)\}/g;
        let match;
        while ((match = nodePattern.exec(fc.content)) !== null) {
          const node = match[1] || match[2] || match[3];
          if (node) flowchartNodes.add(node.trim());
        }
      });

      const sequenceActors = new Set<string>();
      sequences.forEach(seq => {
        const actorPattern = /participant\s+(\w+)/g;
        let match;
        while ((match = actorPattern.exec(seq.content)) !== null) {
          sequenceActors.add(match[1]);
        }
      });

      const intersection = new Set(
        [...flowchartNodes].filter(x => sequenceActors.has(x))
      );

      if (intersection.size === 0 && flowchartNodes.size > 0 && sequenceActors.size > 0) {
        this.warnings.push({
          line: 1,
          type: 'warning',
          rule: 'diagram-logic-inconsistent',
          message: '流程图与时序图之间可能存在逻辑不一致',
          suggestion: '检查两个图表是否描述同一流程，实体命名是否一致'
        });
      }
    }

    const stateDiagrams = this.diagramRegistry.byType.get('state') || [];
    if (stateDiagrams.length > 0) {
      const states = new Set<string>();
      stateDiagrams.forEach(sd => {
        const statePattern = /(\w+)\s*-->/g;
        let match;
        while ((match = statePattern.exec(sd.content)) !== null) {
          states.add(match[1]);
        }
      });

      this.entityRegistry.states.forEach((entity, name) => {
        if (!states.has(name)) {
          this.warnings.push({
            line: entity.line,
            type: 'warning',
            rule: 'state-entity-mismatch',
            message: `实体 "${name}" 在状态图中未找到对应状态`,
            suggestion: '检查状态定义是否完整'
          });
        }
      });
    }
  }

  // ============== 逻辑表达一致性校验 ==============

  private checkLogicalConsistency(): void {
    // 逻辑一致性检查在这里实现
    // 包括步骤编号、状态转换、条件分支等
  }
}
