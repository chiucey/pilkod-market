/**
 * 基础校验模块
 * 
 * 包含标题、目录、链接、图片、表格等基础校验功能
 */

import { BaseValidator, HeadingInfo, TocEntry, ValidationError } from './core';

export class BasicValidator extends BaseValidator {
  private headings: HeadingInfo[] = [];

  validate(): void {
    this.checkHeadings();
    this.checkTocConsistency();
    this.checkLinks();
    this.checkImages();
    this.checkTables();
    this.checkLists();
    this.checkEmptyLines();
  }

  getHeadings(): HeadingInfo[] {
    return this.headings;
  }

  // ============== 标题校验 ==============

  private checkHeadings(): void {
    let h1Count = 0;
    let prevLevel = 0;

    this.lines.forEach((line, index) => {
      // 跳过代码块内的内容
      if (this.isInCodeBlock(index)) return;

      const match = line.match(/^(#{1,6})\s+(.+)$/);
      if (match) {
        const level = match[1].length;
        const text = match[2].trim();
        const id = this.generateHeadingId(text);

        this.headings.push({ level, text, line: index + 1, id });

        if (level === 1) {
          h1Count++;
          // 多个 H1 改为警告而非错误，因为某些大型文档（如多章节指南）可能合理使用多个 H1
          if (h1Count > 1) {
            this.addWarning(
              index + 1,
              'heading-h1-multiple',
              '文档包含多个 H1 标题',
              '建议只保留一个 H1 标题作为文档主标题，或将子章节改为 H2'
            );
          }
        }

        if (prevLevel > 0 && level > prevLevel + 1) {
          this.addWarning(
            index + 1,
            'heading-level-skip',
            `标题层级跳跃：从 H${prevLevel} 直接跳到 H${level}`,
            `建议在 H${prevLevel} 和 H${level} 之间添加 H${prevLevel + 1}`
          );
        }

        prevLevel = level;
      }
    });

    if (this.headings.length > 0 && !this.headings.some(h => h.level === 1)) {
      this.addWarning(
        1,
        'heading-h1-missing',
        '文档缺少 H1 标题',
        '建议在文档开头添加一个 H1 标题'
      );
    }
  }

  // ============== 目录校验 ==============

  private checkTocConsistency(): void {
    const tocPattern = /^##\s+目录|^##\s+Table\s+of\s+Contents/i;
    let inToc = false;
    const tocEntries: TocEntry[] = [];

    this.lines.forEach((line, index) => {
      if (tocPattern.test(line)) {
        inToc = true;
        return;
      }

      if (inToc) {
        if (/^##[^#]/.test(line) || /^```/.test(line)) {
          inToc = false;
          return;
        }

        const tocMatch = line.match(/^(\s*)-\s+\[([^\]]+)\]\(#([^)]+)\)/);
        if (tocMatch) {
          const indent = tocMatch[1].length;
          const level = Math.floor(indent / 2) + 1;
          tocEntries.push({
            text: tocMatch[2],
            level,
            id: tocMatch[3]
          });
        }
      }
    });

    if (tocEntries.length > 0) {
      const headingIds = this.headings.map(h => h.id);

      tocEntries.forEach((entry, index) => {
        if (!headingIds.includes(entry.id)) {
          this.addError(
            index + 1,
            'toc-broken-link',
            `目录项"${entry.text}"指向的标题不存在`,
            '检查标题 ID 是否正确，或更新目录项'
          );
        }
      });

      const tocIds = tocEntries.map(e => e.id);
      this.headings.forEach(heading => {
        if (heading.level > 1 && !tocIds.includes(heading.id)) {
          this.addWarning(
            heading.line,
            'toc-missing-entry',
            `标题"${heading.text}"未出现在目录中`,
            '建议在目录中添加此标题的链接'
          );
        }
      });
    }
  }

  // ============== 链接校验 ==============

  private checkLinks(): void {
    const linkPattern = /\[([^\]]*)\]\(([^)]+)\)/g;

    this.lines.forEach((line, index) => {
      if (this.isInCodeBlock(index)) return;

      let match;
      while ((match = linkPattern.exec(line)) !== null) {
        const text = match[1];
        const url = match[2];

        if (!text.trim()) {
          this.addWarning(
            index + 1,
            'link-empty-text',
            '链接文本为空',
            '为链接添加有意义的文本描述'
          );
        }

        if (url.includes(' ')) {
          this.addError(
            index + 1,
            'link-url-spaces',
            'URL 中包含未编码的空格',
            '使用 %20 编码空格，或用尖括号包裹 URL'
          );
        }
      }
    });
  }

  // ============== 图片校验 ==============

  private checkImages(): void {
    const imgPattern = /!\[([^\]]*)\]\(([^)]+)\)/g;

    this.lines.forEach((line, index) => {
      if (this.isInCodeBlock(index)) return;

      let match;
      while ((match = imgPattern.exec(line)) !== null) {
        const alt = match[1];

        if (!alt.trim()) {
          this.addError(
            index + 1,
            'image-missing-alt',
            '图片缺少替代文本',
            '为图片添加描述性替代文本，提升可访问性'
          );
        }
      }
    });
  }

  // ============== 表格校验 ==============

  private checkTables(): void {
    let inTable = false;
    let columnCount = 0;

    this.lines.forEach((line, index) => {
      // 跳过代码块内的内容
      if (this.isInCodeBlock(index)) return;

      if (line.includes('|')) {
        const cells = line.split('|').filter(c => c.trim() !== '');

        if (!inTable) {
          inTable = true;
          columnCount = cells.length;
        } else {
          // 检查是否是分隔行
          const separatorMatch = line.match(/^\|?\s*[-:|]+\s*\|?$/);
          if (separatorMatch) {
            const separators = line.split('|').filter(c => c.trim() !== '');
            // 只有当分隔行有实际内容时才检查
            if (separators.length > 0 && columnCount > 0 && separators.length !== columnCount) {
              this.addError(
                index + 1,
                'table-separator-mismatch',
                `表格分隔行列数 (${separators.length}) 与表头 (${columnCount}) 不匹配`,
                '确保分隔行列数与表头一致'
              );
            }
          }
        }
      } else if (inTable && line.trim() === '') {
        inTable = false;
      }
    });
  }

  // ============== 列表校验 ==============

  private checkLists(): void {
    let listMarker = '';
    let markerWarningCount = 0;
    const maxListWarnings = 3;

    this.lines.forEach((line, index) => {
      const unorderedMatch = line.match(/^(\s*)([-*+])\s/);

      if (unorderedMatch) {
        const marker = unorderedMatch[2];
        // 只在同一个文档块内检查一致性，且限制警告数量
        if (listMarker && listMarker !== marker && markerWarningCount < maxListWarnings) {
          markerWarningCount++;
          this.addWarning(
            index + 1,
            'list-marker-inconsistent',
            `列表标记符号不一致: 使用了 "${listMarker}" 和 "${marker}"`,
            '统一使用相同的列表标记符号'
          );
        }
        listMarker = marker;
      }
    });
  }

  // ============== 空行校验 ==============

  private checkEmptyLines(): void {
    let consecutiveEmptyLines = 0;

    this.lines.forEach((line, index) => {
      if (line.trim() === '') {
        consecutiveEmptyLines++;
        if (consecutiveEmptyLines > 2) {
          this.addWarning(
            index + 1,
            'excessive-empty-lines',
            '存在过多连续空行',
            '建议最多保留一个空行'
          );
        }
      } else {
        consecutiveEmptyLines = 0;
      }
    });
  }
}
