/**
 * 工作流图表完整性校验模块
 * 
 * 包含流程图、时序图、用例图、状态图的完整性校验
 */

import { DiagramRegistry, DiagramInfo } from './core';

export class WorkflowValidator {
  private errors: any[] = [];
  private warnings: any[] = [];
  private info: any[] = [];
  private diagramRegistry: DiagramRegistry;

  constructor(diagramRegistry: DiagramRegistry) {
    this.diagramRegistry = diagramRegistry;
  }

  validate(): { errors: any[]; warnings: any[]; info: any[] } {
    this.errors = [];
    this.warnings = [];
    this.info = [];

    this.checkFlowchartCompleteness();
    this.checkSequenceDiagramCompleteness();
    this.checkUsecaseDiagramCompleteness();
    this.checkStateDiagramCompleteness();

    return {
      errors: this.errors,
      warnings: this.warnings,
      info: this.info
    };
  }

  // ============== 流程图完整性校验 ==============

  private checkFlowchartCompleteness(): void {
    const flowcharts = this.diagramRegistry.byType.get('flowchart') || [];

    flowcharts.forEach(diagram => {
      const content = diagram.content;

      // 检查起点
      const hasStart = /\(\s*\)|\[\s*\]|\[\*\]/.test(content) ||
        /start|begin|开始/i.test(content);

      // 检查终点
      const hasEnd = /\(\s*\)|\[\s*\]|\[\*\]/.test(content) ||
        /end|stop|结束/i.test(content);

      // 检查分支完整性
      const altCount = (content.match(/\balt\b/gi) || []).length;
      const elseCount = (content.match(/\belse\b/gi) || []).length;
      const endCount = (content.match(/\bend\b/gi) || []).length;

      if (altCount > 0 && elseCount < altCount) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'flowchart-incomplete-branch',
          message: '流程图存在未处理的分支（缺少 else 分支）',
          suggestion: '为每个 alt 分支添加 else 处理'
        });
      }

      if (altCount > 0 && endCount < altCount) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'flowchart-unclosed-alt',
          message: '流程图 alt 块未正确闭合',
          suggestion: '添加 end 关闭 alt 块'
        });
      }

      // 检查节点可达性
      const nodes = this.extractFlowchartNodes(content);
      const edges = this.extractFlowchartEdges(content);

      const connectedNodes = new Set<string>();
      edges.forEach(edge => {
        connectedNodes.add(edge.from);
        connectedNodes.add(edge.to);
      });

      nodes.forEach(node => {
        if (!connectedNodes.has(node.id) && nodes.length > 1) {
          this.info.push({
            line: diagram.line,
            type: 'info',
            rule: 'flowchart-isolated-node',
            message: `流程图节点 "${node.label || node.id}" 可能是孤立节点`,
            suggestion: '检查节点是否有连接'
          });
        }
      });

      // 更新完整性信息
      diagram.completeness = {
        hasStart,
        hasEnd,
        hasBranches: altCount > 0,
        branchesComplete: elseCount >= altCount,
        allNodesReachable: connectedNodes.size === nodes.length,
        participantCount: 0,
        messageCount: 0,
        actorCount: 0,
        usecaseCount: 0
      };

      if (!hasStart) {
        this.info.push({
          line: diagram.line,
          type: 'info',
          rule: 'flowchart-missing-start',
          message: '流程图缺少明确的起点',
          suggestion: '添加起点节点，如 ([开始]) 或 [*]'
        });
      }

      if (!hasEnd) {
        this.info.push({
          line: diagram.line,
          type: 'info',
          rule: 'flowchart-missing-end',
          message: '流程图缺少明确的终点',
          suggestion: '添加终点节点，如 ([结束]) 或 [*]'
        });
      }
    });
  }

  private extractFlowchartNodes(content: string): Array<{ id: string; label?: string }> {
    const nodes: Array<{ id: string; label?: string }> = [];
    const seen = new Set<string>();

    const patterns = [
      /(\w+)\[([^\]]+)\]/g,
      /(\w+)\(([^)]+)\)/g,
      /(\w+)\{([^}]+)\}/g,
    ];

    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const id = match[1];
        if (!seen.has(id)) {
          seen.add(id);
          nodes.push({ id, label: match[2] });
        }
      }
    });

    return nodes;
  }

  private extractFlowchartEdges(content: string): Array<{ from: string; to: string }> {
    const edges: Array<{ from: string; to: string }> = [];
    const edgePattern = /(\w+)\s*--?>?\s*<?-?-?-?\s*(\w+)/g;
    let match;
    while ((match = edgePattern.exec(content)) !== null) {
      edges.push({ from: match[1], to: match[2] });
    }
    return edges;
  }

  // ============== 时序图完整性校验 ==============

  private checkSequenceDiagramCompleteness(): void {
    const sequences = this.diagramRegistry.byType.get('sequence') || [];

    sequences.forEach(diagram => {
      const content = diagram.content;

      // 提取参与者
      const participants: string[] = [];
      const participantPattern = /participant\s+(\w+)/gi;
      let match;
      while ((match = participantPattern.exec(content)) !== null) {
        participants.push(match[1]);
      }

      // 提取 actor
      const actorPattern = /actor\s+(\w+)/gi;
      while ((match = actorPattern.exec(content)) !== null) {
        participants.push(match[1]);
      }

      // 提取消息
      const messages: Array<{ from: string; to: string }> = [];
      const messagePattern = /(\w+)\s*->>?-?\s*(\w+)/g;
      while ((match = messagePattern.exec(content)) !== null) {
        messages.push({ from: match[1], to: match[2] });
      }

      // 检查 alt/else 配对
      const altCount = (content.match(/\balt\b/gi) || []).length;
      const elseCount = (content.match(/\belse\b/gi) || []).length;
      const endCount = (content.match(/\bend\b/gi) || []).length;

      if (altCount > 0 && elseCount < altCount) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'sequence-incomplete-branch',
          message: '时序图存在未处理的分支',
          suggestion: '为每个 alt 分支添加 else 处理'
        });
      }

      if (altCount > 0 && endCount < altCount) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'sequence-unclosed-alt',
          message: '时序图 alt 块未正确闭合',
          suggestion: '添加 end 关闭 alt 块'
        });
      }

      if (participants.length > 1 && messages.length === 0) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'sequence-no-messages',
          message: '时序图定义了参与者但没有消息',
          suggestion: '添加参与者之间的消息交互'
        });
      }

      // 检查未参与交互的参与者
      const activeParticipants = new Set<string>();
      messages.forEach(msg => {
        activeParticipants.add(msg.from);
        activeParticipants.add(msg.to);
      });

      participants.forEach(p => {
        if (!activeParticipants.has(p) && participants.length > 1) {
          this.warnings.push({
            line: diagram.line,
            type: 'warning',
            rule: 'sequence-inactive-participant',
            message: `参与者 "${p}" 未参与任何消息交互`,
            suggestion: '检查是否遗漏了消息，或移除该参与者'
          });
        }
      });

      diagram.completeness = {
        hasStart: true,
        hasEnd: true,
        hasBranches: altCount > 0,
        branchesComplete: elseCount >= altCount,
        allNodesReachable: true,
        participantCount: participants.length,
        messageCount: messages.length,
        actorCount: participants.length,
        usecaseCount: 0
      };
    });
  }

  // ============== 用例图完整性校验 ==============

  private checkUsecaseDiagramCompleteness(): void {
    const usecases = this.diagramRegistry.byType.get('usecase') || [];

    usecases.forEach(diagram => {
      const content = diagram.content;

      // 提取 actors
      const actors: string[] = [];
      const actorPattern = /actor\s+(\w+)/gi;
      let match;
      while ((match = actorPattern.exec(content)) !== null) {
        actors.push(match[1]);
      }

      // 提取 use cases
      const useCaseList: string[] = [];
      const usecasePattern = /usecase\s+["']?([^"'\n]+)["']?/gi;
      while ((match = usecasePattern.exec(content)) !== null) {
        useCaseList.push(match[1]);
      }

      // 提取圆括号中的用例
      const parenUseCasePattern = /\(([^)]+)\)/g;
      while ((match = parenUseCasePattern.exec(content)) !== null) {
        if (match[1].length > 3) {
          useCaseList.push(match[1]);
        }
      }

      if (actors.length === 0) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'usecase-no-actor',
          message: '用例图缺少参与者（actor）',
          suggestion: '添加参与者，如 actor User'
        });
      }

      if (useCaseList.length === 0) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'usecase-no-usecase',
          message: '用例图缺少用例',
          suggestion: '添加用例，如 usecase Login 或 (登录)'
        });
      }

      // 检查关系
      const relationPattern = /(\w+)\s*-->\s*(\(|\w)/g;
      const relations = content.match(relationPattern) || [];

      if (actors.length > 0 && useCaseList.length > 0 && relations.length === 0) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'usecase-no-relations',
          message: '用例图缺少参与者与用例之间的关系',
          suggestion: '添加关系，如 User --> (Login)'
        });
      }

      diagram.completeness = {
        hasStart: true,
        hasEnd: true,
        hasBranches: false,
        branchesComplete: true,
        allNodesReachable: true,
        participantCount: 0,
        messageCount: 0,
        actorCount: actors.length,
        usecaseCount: useCaseList.length
      };
    });
  }

  // ============== 状态图完整性校验 ==============

  private checkStateDiagramCompleteness(): void {
    const states = this.diagramRegistry.byType.get('state') || [];

    states.forEach(diagram => {
      const content = diagram.content;

      const hasInitialState = /\[\*\]/.test(content) || /初始|开始/i.test(content);
      const hasFinalState = /\[\*\]/.test(content) || /终止|结束/i.test(content);

      // 提取状态
      const stateList: string[] = [];
      const statePattern = /state\s+"?([^"\n:]+)"?/gi;
      let match;
      while ((match = statePattern.exec(content)) !== null) {
        stateList.push(match[1]);
      }

      // 提取转换
      const transitions: Array<{ from: string; to: string }> = [];
      const transitionPattern = /(\w+|\[\*\])\s*-->\s*(\w+|\[\*\])/g;
      while ((match = transitionPattern.exec(content)) !== null) {
        transitions.push({ from: match[1], to: match[2] });
      }

      if (stateList.length > 0 && transitions.length === 0) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'state-no-transitions',
          message: '状态图定义了状态但没有转换',
          suggestion: '添加状态之间的转换，如 Pending --> Approved'
        });
      }

      if (!hasInitialState) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'state-missing-initial',
          message: '状态图缺少初始状态',
          suggestion: '添加初始状态 [*]'
        });
      }

      if (!hasFinalState) {
        this.warnings.push({
          line: diagram.line,
          type: 'warning',
          rule: 'state-missing-final',
          message: '状态图缺少终止状态',
          suggestion: '添加终止状态 [*]'
        });
      }

      diagram.completeness = {
        hasStart: hasInitialState,
        hasEnd: hasFinalState,
        hasBranches: false,
        branchesComplete: true,
        allNodesReachable: true,
        participantCount: 0,
        messageCount: transitions.length,
        actorCount: 0,
        usecaseCount: stateList.length
      };
    });
  }
}
