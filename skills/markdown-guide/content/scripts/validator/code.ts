/**
 * 代码块校验模块
 * 
 * 包含语言类型校验、拼写检查、语法检查、嵌套 Markdown 检测
 */

import { BaseValidator, CodeBlockInfo, SpellingError, SyntaxError } from './core';

// ============== 常量定义 ==============

const COMMON_ENGLISH_WORDS = new Set([
  'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
  'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
  'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
  'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
  'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
  'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
  'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
  'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
  'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
  'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
  'function', 'variable', 'const', 'let', 'var', 'class', 'interface', 'type',
  'string', 'number', 'boolean', 'object', 'array', 'null', 'undefined', 'void',
  'return', 'import', 'export', 'default', 'from', 'async', 'await', 'promise',
  'module', 'package', 'library', 'framework', 'component', 'service', 'controller',
  'server', 'client', 'api', 'http', 'https', 'url', 'uri', 'endpoint',
  'user', 'password', 'email', 'name', 'id', 'uuid', 'timestamp', 'date',
  'file', 'path', 'directory', 'folder', 'read', 'write', 'create', 'delete',
  'true', 'false', 'yes', 'no', 'ok', 'cancel', 'submit', 'reset', 'clear',
]);

const PROGRAMMING_KEYWORDS = new Set([
  'const', 'let', 'var', 'function', 'class', 'interface', 'type', 'enum',
  'extends', 'implements', 'import', 'export', 'from', 'as', 'default',
  'async', 'await', 'yield', 'return', 'throw', 'try', 'catch', 'finally',
  'if', 'else', 'switch', 'case', 'break', 'continue', 'for', 'while', 'do',
  'in', 'of', 'new', 'delete', 'typeof', 'instanceof', 'void', 'null', 'undefined',
  'true', 'false', 'this', 'super', 'static', 'public', 'private', 'protected',
  'def', 'class', 'import', 'from', 'as', 'pass', 'lambda', 'with',
  'yield', 'global', 'nonlocal', 'assert', 'raise', 'try', 'except', 'finally',
  'elif', 'and', 'or', 'not', 'is', 'self', 'cls',
  'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN',
  'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'DROP',
  'ALTER', 'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'GRANT', 'REVOKE',
]);

const VALID_LANGUAGES = new Set([
  'javascript', 'js', 'typescript', 'ts', 'python', 'py', 'java', 'c', 'cpp', 'c++',
  'csharp', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala',
  'sql', 'mysql', 'postgresql', 'pgsql', 'sqlite', 'oracle', 'plsql',
  'html', 'xml', 'xhtml', 'svg', 'css', 'scss', 'sass', 'less', 'stylus',
  'markdown', 'md', 'mdown', 'mkd', 'rst', 'asciidoc', 'adoc',
  'json', 'yaml', 'yml', 'toml', 'ini', 'conf', 'config', 'properties',
  'graphql', 'gql', 'protobuf', 'proto', 'dockerfile', 'docker', 'makefile',
  'mermaid', 'plantuml', 'dot', 'graphviz',
  'text', 'plaintext', 'txt', 'log', 'diff', 'patch', 'shell', 'bash', 'sh', 'zsh',
  'http', 'curl', 'rest', 'api',
  // DevOps & Infrastructure
  'nginx', 'apache', 'promql', 'hcl', 'terraform', 'ansible', 'kubernetes', 'k8s', 'helm',
  'docker-compose', 'yaml-compose',
  // Data & Query
  'cypher', 'gremlin', 'sparql',
  // Markup & Documentation
  'latex', 'tex', 'bibtex',
  // Other common
  'regex', 'regexp', 'lua', 'perl', 'r', 'julia', 'matlab',
  'objc', 'objectivec', 'swift', 'dart', 'elixir', 'erlang', 'haskell', 'lisp', 'clojure',
]);

export class CodeValidator extends BaseValidator {
  private codeBlocks: CodeBlockInfo[] = [];

  validate(): void {
    this.checkCodeBlocks();
  }

  getCodeBlocks(): CodeBlockInfo[] {
    return this.codeBlocks;
  }

  // ============== 代码块检查 ==============

  private checkCodeBlocks(): void {
    let inCodeBlock = false;
    let codeBlockStart = 0;
    let codeBlockFence = '';
    let codeBlockLanguage = '';
    let codeBlockContent: string[] = [];

    this.lines.forEach((line, index) => {
      const fenceMatch = line.match(/^(>{3,}|`{3,}|~{3,})(\w*)/);

      if (fenceMatch && !inCodeBlock) {
        inCodeBlock = true;
        codeBlockStart = index + 1;
        codeBlockFence = fenceMatch[1];
        codeBlockLanguage = fenceMatch[2] || '';
        codeBlockContent = [];

        if ((fenceMatch[1].startsWith('```') || fenceMatch[1].startsWith('~~~')) && !fenceMatch[2]) {
          this.addWarning(
            index + 1,
            'codeblock-missing-lang',
            '代码块未指定语言标识',
            '添加语言标识以启用语法高亮和校验'
          );
        } else if (fenceMatch[2] && !VALID_LANGUAGES.has(fenceMatch[2].toLowerCase())) {
          this.addWarning(
            index + 1,
            'codeblock-unknown-language',
            `未知的代码块语言标识: "${fenceMatch[2]}"`,
            '使用标准的语言标识，如 javascript、python、json 等'
          );
        }
      } else if (inCodeBlock) {
        if (line.match(/^[`~]{3,}$/) || (codeBlockFence && line.startsWith(codeBlockFence[0].repeat(3)))) {
          const content = codeBlockContent.join('\n');

          const blockInfo: CodeBlockInfo = {
            line: codeBlockStart,
            language: codeBlockLanguage,
            content: content,
            hasLanguageTag: !!codeBlockLanguage,
            spellingErrors: [],
            syntaxErrors: [],
            nestedMarkdown: false
          };

          if (this.shouldCheckSpelling(codeBlockLanguage)) {
            blockInfo.spellingErrors = this.checkSpelling(content, codeBlockStart);
          }

          if (codeBlockLanguage) {
            blockInfo.syntaxErrors = this.checkSyntax(content, codeBlockLanguage, codeBlockStart);
          }

          blockInfo.nestedMarkdown = this.detectNestedMarkdown(content);

          this.codeBlocks.push(blockInfo);
          inCodeBlock = false;
          codeBlockLanguage = '';
        } else {
          codeBlockContent.push(line);
        }
      }
    });

    if (inCodeBlock) {
      this.addError(
        codeBlockStart,
        'codeblock-unclosed',
        '代码块未正确闭合',
        `在代码块末尾添加 ${codeBlockFence}`
      );
    }
  }

  // ============== 拼写检查 ==============

  private shouldCheckSpelling(language: string): boolean {
    const textLanguages = new Set(['text', 'plaintext', 'txt', 'markdown', 'md', 'rst', 'asciidoc']);
    return textLanguages.has(language.toLowerCase());
  }

  private checkSpelling(content: string, startLine: number): SpellingError[] {
    const errors: SpellingError[] = [];
    const lines = content.split('\n');

    lines.forEach((line, lineIndex) => {
      const words = line.match(/\b[a-zA-Z]{3,}\b/g) || [];

      words.forEach(word => {
        const lowerWord = word.toLowerCase();
        if (PROGRAMMING_KEYWORDS.has(word) || PROGRAMMING_KEYWORDS.has(lowerWord)) return;
        if (COMMON_ENGLISH_WORDS.has(lowerWord)) return;
        if (/[A-Z]/.test(word.slice(1)) || word.includes('_')) return;

        const column = line.indexOf(word) + 1;
        errors.push({
          word: word,
          line: startLine + lineIndex,
          column: column,
          suggestions: this.getSpellingSuggestions(word)
        });
      });
    });

    errors.forEach(err => {
      this.addWarning(
        err.line,
        'spelling-error',
        `可能的拼写错误: "${err.word}"`,
        err.suggestions.length > 0 ? `可能的正确拼写: ${err.suggestions.join(', ')}` : '请检查拼写'
      );
    });

    return errors;
  }

  private getSpellingSuggestions(word: string): string[] {
    const suggestions: string[] = [];
    const common: Record<string, string[]> = {
      'teh': ['the'], 'adn': ['and'], 'taht': ['that'], 'woudl': ['would'],
      'recieve': ['receive'], 'occured': ['occurred'], 'seperate': ['separate'],
      'definately': ['definitely'], 'accomodate': ['accommodate'],
      'enviroment': ['environment'], 'goverment': ['government'],
      'knowlege': ['knowledge'], 'begining': ['beginning'],
    };
    if (common[word.toLowerCase()]) {
      suggestions.push(...common[word.toLowerCase()]);
    }
    return suggestions;
  }

  // ============== 语法检查 ==============

  private checkSyntax(content: string, language: string, startLine: number): SyntaxError[] {
    const normalizedLang = language.toLowerCase();
    const errors: SyntaxError[] = [];

    switch (normalizedLang) {
      case 'json':
        errors.push(...this.checkJsonSyntax(content, startLine));
        break;
      case 'yaml':
      case 'yml':
        errors.push(...this.checkYamlSyntax(content, startLine));
        break;
      case 'sql':
        errors.push(...this.checkSqlSyntax(content, startLine));
        break;
      case 'javascript':
      case 'js':
      case 'typescript':
      case 'ts':
        errors.push(...this.checkJsTsSyntax(content, startLine));
        break;
      case 'python':
      case 'py':
        errors.push(...this.checkPythonSyntax(content, startLine));
        break;
      case 'html':
      case 'xml':
        errors.push(...this.checkHtmlXmlSyntax(content, startLine));
        break;
      case 'css':
      case 'scss':
        errors.push(...this.checkCssSyntax(content, startLine));
        break;
    }

    errors.forEach(err => {
      if (err.severity === 'error') {
        this.addError(err.line, 'syntax-error', `语法错误: ${err.message}`, '检查语法并修正');
      } else {
        this.addWarning(err.line, 'syntax-warning', `语法警告: ${err.message}`, '检查语法');
      }
    });

    return errors;
  }

  private checkJsonSyntax(content: string, startLine: number): SyntaxError[] {
    const errors: SyntaxError[] = [];
    try {
      JSON.parse(content);
    } catch (e: any) {
      const match = e.message.match(/position\s+(\d+)/);
      if (match) {
        const position = parseInt(match[1]);
        const beforeError = content.substring(0, position);
        const lineNum = beforeError.split('\n').length;
        errors.push({
          line: startLine + lineNum - 1,
          column: beforeError.split('\n').pop()?.length || 0,
          message: e.message,
          severity: 'error'
        });
      }
    }
    return errors;
  }

  private checkYamlSyntax(content: string, startLine: number): SyntaxError[] {
    const errors: SyntaxError[] = [];
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      // 检查 Tab 缩进（严重问题）
      if (line.includes('\t') && line.trim().length > 0) {
        const leadingTabs = line.match(/^\t+/);
        if (leadingTabs) {
          errors.push({
            line: startLine + index,
            column: 1,
            message: 'YAML 应使用空格缩进，而非 Tab',
            severity: 'warning'
          });
        }
      }
      // 移除冒号后空格检查，因为在某些 YAML 变体中是允许的
    });
    return errors;
  }

  private checkSqlSyntax(content: string, startLine: number): SyntaxError[] {
    const errors: SyntaxError[] = [];
    const openParens = (content.match(/\(/g) || []).length;
    const closeParens = (content.match(/\)/g) || []).length;

    if (openParens !== closeParens) {
      errors.push({
        line: startLine,
        column: 1,
        message: `括号不匹配: ${openParens} 个 "(" 和 ${closeParens} 个 ")"`,
        severity: 'error'
      });
    }
    return errors;
  }

  private checkJsTsSyntax(content: string, startLine: number): SyntaxError[] {
    const errors: SyntaxError[] = [];
    const brackets = [
      { open: '(', close: ')' },
      { open: '[', close: ']' },
      { open: '{', close: '}' }
    ];

    brackets.forEach(({ open, close }) => {
      const openCount = (content.match(new RegExp(`\\${open}`, 'g')) || []).length;
      const closeCount = (content.match(new RegExp(`\\${close}`, 'g')) || []).length;

      if (openCount !== closeCount) {
        errors.push({
          line: startLine,
          column: 1,
          message: `${open}${close} 括号不匹配`,
          severity: 'error'
        });
      }
    });
    return errors;
  }

  private checkPythonSyntax(content: string, startLine: number): SyntaxError[] {
    const errors: SyntaxError[] = [];
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      if (line.includes('\t') && line.includes(' ') && !line.startsWith('\t')) {
        errors.push({
          line: startLine + index,
          column: 1,
          message: '缩进不应混用 Tab 和空格',
          severity: 'warning'
        });
      }
    });
    return errors;
  }

  private checkHtmlXmlSyntax(content: string, startLine: number): SyntaxError[] {
    const errors: SyntaxError[] = [];
    const tagStack: { tag: string; line: number }[] = [];
    const tagPattern = /<\/?([a-zA-Z][a-zA-Z0-9]*)[^>]*>/g;
    const selfClosing = new Set(['br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr']);
    const lines = content.split('\n');

    lines.forEach((line, lineIndex) => {
      let match;
      while ((match = tagPattern.exec(line)) !== null) {
        const fullMatch = match[0];
        const tagName = match[1].toLowerCase();

        if (fullMatch.endsWith('/>') || selfClosing.has(tagName)) continue;

        if (fullMatch.startsWith('</')) {
          if (tagStack.length === 0) {
            errors.push({
              line: startLine + lineIndex,
              column: match.index + 1,
              message: `多余的闭合标签 </${tagName}>`,
              severity: 'error'
            });
          } else {
            const lastTag = tagStack.pop()!;
            if (lastTag.tag !== tagName) {
              errors.push({
                line: startLine + lineIndex,
                column: match.index + 1,
                message: `标签不匹配: 期望 </${lastTag.tag}>，实际 </${tagName}>`,
                severity: 'error'
              });
            }
          }
        } else {
          tagStack.push({ tag: tagName, line: startLine + lineIndex });
        }
      }
    });

    tagStack.forEach(({ tag, line }) => {
      errors.push({
        line: line,
        column: 1,
        message: `标签 <${tag}> 未闭合`,
        severity: 'error'
      });
    });

    return errors;
  }

  private checkCssSyntax(content: string, startLine: number): SyntaxError[] {
    const errors: SyntaxError[] = [];
    const openBraces = (content.match(/{/g) || []).length;
    const closeBraces = (content.match(/}/g) || []).length;

    if (openBraces !== closeBraces) {
      errors.push({
        line: startLine,
        column: 1,
        message: `大括号不匹配: ${openBraces} 个 "{" 和 ${closeBraces} 个 "}"`,
        severity: 'error'
      });
    }
    return errors;
  }

  // ============== 嵌套 Markdown 检测 ==============

  private detectNestedMarkdown(content: string): boolean {
    const patterns = [
      /^#{1,6}\s+\S+/,
      /\[.+\]\(.+\)/,
      /!\[.+\]\(.+\)/,
      /^\s*[-*+]\s+\S+/,
      /^\s*\d+\.\s+\S+/,
      /\|.+\|/,
    ];

    const lines = content.split('\n');
    let matchCount = 0;

    lines.forEach(line => {
      patterns.forEach(pattern => {
        if (pattern.test(line)) matchCount++;
      });
    });

    return matchCount >= 3;
  }
}
