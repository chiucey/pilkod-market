/**
 * PDF 文档提取器
 */

import fs from 'fs-extra';
import path from 'path';
import type { PDFExtractionOptions, PDFExtractionResult, CrawledPage } from './types.js';

// 动态导入 pdf-parse（可选依赖）
async function loadPdfParse() {
  try {
    const pdfParse = await import('pdf-parse');
    return pdfParse.default || pdfParse;
  } catch (err) {
    throw new Error(
      '❌ pdf-parse 未安装。请运行: npm install pdf-parse\n' +
      '   如果不需要 PDF 功能，可以使用网页爬虫（移除 --pdf 参数）'
    );
  }
}

export class PDFExtractor {
  /**
   * 从 PDF 文件提取内容
   */
  async extractFromPDF(
    pdfPath: string,
    options: PDFExtractionOptions = {}
  ): Promise<PDFExtractionResult> {
    console.log(`📄 开始提取 PDF: ${pdfPath}`);

    // 动态加载 pdf-parse
    const pdfParse = await loadPdfParse();

    // 读取 PDF 文件
    const dataBuffer = await fs.readFile(pdfPath);

    // 基础提取
    const data = await pdfParse(dataBuffer);

    const result: PDFExtractionResult = {
      text: data.text,
      pages: data.numpages,
      metadata: data.metadata || {}
    };

    console.log(`✅ PDF 提取完成: ${result.pages} 页`);

    return result;
  }

  /**
   * 将 PDF 提取结果转换为 CrawledPage 格式
   */
  convertToCrawledPage(
    pdfPath: string,
    extractionResult: PDFExtractionResult,
    name: string
  ): CrawledPage {
    const title = extractionResult.metadata?.Title || 
                  path.basename(pdfPath, '.pdf');

    // 分割文本为段落
    const paragraphs = extractionResult.text
      .split('\n\n')
      .filter(p => p.trim().length > 0);

    // 转换为 Markdown
    const content = paragraphs
      .map(p => p.trim().replace(/\n/g, ' '))
      .join('\n\n');

    // 提取代码块（简单启发式）
    const codeExamples = this.extractCodeFromText(extractionResult.text);

    return {
      url: `file://${pdfPath}`,
      title,
      content,
      htmlContent: `<pre>${extractionResult.text}</pre>`,
      codeExamples,
      category: 'pdf-document',
      scrapedAt: new Date().toISOString(),
      links: []
    };
  }

  /**
   * 从文本中提取代码块
   */
  private extractCodeFromText(text: string): Array<{
    language: string;
    content: string;
    lineCount: number;
  }> {
    const codeExamples: Array<{
      language: string;
      content: string;
      lineCount: number;
    }> = [];

    // 检测代码块模式
    const codePatterns = [
      // 常见的代码标记
      /```(\w+)?\n([\s\S]+?)```/g,
      // 缩进的代码块
      /((?:^    .+$\n?)+)/gm
    ];

    for (const pattern of codePatterns) {
      let match;
      while ((match = pattern.exec(text)) !== null) {
        const language = match[1] || 'text';
        const content = (match[2] || match[1] || '').trim();
        
        if (content.length > 10 && content.length < 5000) {
          codeExamples.push({
            language,
            content,
            lineCount: content.split('\n').length
          });
        }
      }
    }

    return codeExamples.slice(0, 20);
  }

  /**
   * 保存提取结果
   */
  async saveExtraction(
    outputDir: string,
    name: string,
    page: CrawledPage
  ): Promise<void> {
    await fs.ensureDir(outputDir);

    // 保存为 JSON
    const pagesDir = path.join(outputDir, 'pages');
    await fs.ensureDir(pagesDir);
    await fs.writeJSON(
      path.join(pagesDir, '001-pdf-content.json'),
      page,
      { spaces: 2 }
    );

    // 保存摘要
    const summary = {
      name,
      baseUrl: page.url,
      totalPages: 1,
      categories: { 'pdf-document': 1 },
      crawledAt: page.scrapedAt
    };

    await fs.writeJSON(
      path.join(outputDir, 'summary.json'),
      summary,
      { spaces: 2 }
    );

    // 保存为 Markdown
    const mdPath = path.join(outputDir, `${name}.md`);
    await fs.writeFile(mdPath, `# ${page.title}\n\n${page.content}`);

    console.log(`💾 PDF 提取结果已保存: ${outputDir}`);
  }
}

