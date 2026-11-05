/**
 * 爬虫管理器 - 统一入口，自动选择合适的爬虫
 */

import fs from 'fs-extra';
import path from 'path';
import { DocumentationCrawler } from './doc-crawler.js';
import { DynamicCrawler } from './dynamic-crawler.js';
import { PDFExtractor } from './pdf-extractor.js';
import { KnowledgeConverter } from './knowledge-converter.js';
import { ProgressBar } from './progress-bar.js';
import type { CrawlerConfig, CrawlResult } from './types.js';

export interface CrawlOptions {
  name: string;
  url?: string;
  pdfPath?: string;
  outputDir: string;
  useDynamic?: boolean;
  maxPages?: number;
  concurrency?: number;
}

export class CrawlerManager {
  /**
   * 执行爬取
   */
  async executeCrawl(options: CrawlOptions): Promise<CrawlResult | null> {
    console.log(`\n🚀 开始文档爬取任务`);
    console.log(`📝 项目: ${options.name}`);

    // PDF 模式
    if (options.pdfPath) {
      return await this.crawlPDF(options);
    }

    // 网页爬取模式
    if (options.url) {
      return await this.crawlWebsite(options);
    }

    console.error('❌ 错误: 必须提供 url 或 pdfPath');
    return null;
  }

  /**
   * 爬取网站
   */
  private async crawlWebsite(options: CrawlOptions): Promise<CrawlResult> {
    const config: CrawlerConfig = {
      name: options.name,
      baseUrl: options.url!,
      maxPages: options.maxPages || 200,
      concurrency: options.concurrency || 5
    };

    // 选择爬虫类型
    const crawler = options.useDynamic 
      ? new DynamicCrawler(config)
      : new DocumentationCrawler(config);

    const crawlerType = options.useDynamic ? '动态爬虫 (Puppeteer)' : '静态爬虫';
    console.log(`🔧 使用: ${crawlerType}`);

    // 进度条
    const progressBar = new ProgressBar();

    // 开始爬取
    const result = await crawler.crawl((progress) => {
      progressBar.update(progress);
    });

    progressBar.complete(result.duration, result.totalPages);

    // 保存原始数据
    const rawDir = path.join(options.outputDir, 'raw', options.name);
    await crawler.saveResults(rawDir);

    // 转换为知识库
    await this.convertAndIndex(options.name, rawDir, options.outputDir);

    // 显示报告
    this.showReport(result, options);

    return result;
  }

  /**
   * 爬取 PDF
   */
  private async crawlPDF(options: CrawlOptions): Promise<CrawlResult> {
    console.log(`📄 PDF 模式`);
    console.log(`📂 文件: ${options.pdfPath}`);

    const extractor = new PDFExtractor();
    
    // 提取 PDF
    const extractionResult = await extractor.extractFromPDF(options.pdfPath!);
    
    // 转换为 CrawledPage 格式
    const page = extractor.convertToCrawledPage(
      options.pdfPath!,
      extractionResult,
      options.name
    );

    // 保存
    const rawDir = path.join(options.outputDir, 'raw', options.name);
    await extractor.saveExtraction(rawDir, options.name, page);

    // 转换为知识库
    await this.convertAndIndex(options.name, rawDir, options.outputDir);

    // 构造结果
    const result: CrawlResult = {
      pages: [page],
      totalPages: 1,
      duration: 0,
      categories: { 'pdf-document': [page] }
    };

    this.showReport(result, options);

    return result;
  }

  /**
   * 转换为知识库
   */
  private async convertAndIndex(
    name: string,
    rawDir: string,
    outputDir: string
  ): Promise<void> {
    console.log(`\n🔄 转换知识库...`);

    // 转换为 Markdown
    const indexedDir = path.join(outputDir, 'indexed');
    await fs.ensureDir(indexedDir);

    const converter = new KnowledgeConverter();
    await converter.convertToKnowledgeBase(rawDir, indexedDir);

    console.log(`✅ 知识库转换完成`);
  }

  /**
   * 显示报告
   */
  private showReport(result: CrawlResult, options: CrawlOptions): void {
    console.log(`\n📊 爬取报告`);
    console.log(`${'='.repeat(50)}`);
    console.log(`📝 项目名称: ${options.name}`);
    console.log(`📄 总页数: ${result.totalPages}`);
    console.log(`⏱️  用时: ${this.formatDuration(result.duration)}`);
    console.log(`📂 分类数: ${Object.keys(result.categories).length}`);

    console.log(`\n📚 分类统计:`);
    for (const [category, pages] of Object.entries(result.categories)) {
      console.log(`  - ${this.formatCategoryName(category)}: ${pages.length} 页`);
    }

    console.log(`\n💾 存储位置:`);
    console.log(`  - 原始数据: ${path.join(options.outputDir, 'raw', options.name)}`);
    console.log(`  - 知识库: ${path.join(options.outputDir, 'indexed')}`);

    console.log(`\n💡 使用方式:`);
    console.log(`  1. 查看索引: cat ${path.join(options.outputDir, 'indexed', options.name)}-index.md`);
    console.log(`  2. AI 写作时会自动读取知识库 Markdown 文件`);
    
    console.log(`\n✅ 任务完成!\n`);
  }

  /**
   * 格式化分类名称
   */
  private formatCategoryName(category: string): string {
    const names: Record<string, string> = {
      'getting-started': '入门指南',
      'guide': '使用指南',
      'api': 'API 参考',
      'examples': '示例代码',
      'advanced': '进阶内容',
      'migration': '迁移指南',
      'pdf-document': 'PDF 文档',
      'other': '其他'
    };

    return names[category] || category;
  }

  /**
   * 格式化持续时间
   */
  private formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}小时${minutes % 60}分`;
    }
    if (minutes > 0) {
      return `${minutes}分${seconds % 60}秒`;
    }
    return `${seconds}秒`;
  }

  /**
   * 检测是否为动态页面
   */
  static isDynamicSite(url: string): boolean {
    const dynamicPatterns = [
      'react',
      'vue',
      'angular',
      'svelte',
      'next.js',
      'nuxt',
      'spa'
    ];

    const lowerUrl = url.toLowerCase();
    return dynamicPatterns.some(pattern => lowerUrl.includes(pattern));
  }
}

