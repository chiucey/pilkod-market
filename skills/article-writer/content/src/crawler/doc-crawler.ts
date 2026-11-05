/**
 * 文档爬虫 - 静态页面爬取
 */

import axios from 'axios';
import * as cheerio from 'cheerio';
import TurndownService from 'turndown';
import { URL } from 'url';
import pLimit from 'p-limit';
import fs from 'fs-extra';
import path from 'path';
import type {
  CrawlerConfig,
  CrawledPage,
  CodeExample,
  CrawlProgress,
  CrawlResult,
  CrawlSummary
} from './types.js';

export class DocumentationCrawler {
  protected config: CrawlerConfig;
  protected visitedUrls = new Set<string>();
  protected urlQueue: string[] = [];
  protected crawledPages: CrawledPage[] = [];
  protected turndownService: TurndownService;
  protected limit: ReturnType<typeof pLimit>;
  protected startTime = 0;

  constructor(config: CrawlerConfig) {
    this.config = {
      maxPages: 100,
      concurrency: 5,
      rateLimit: 500,
      timeout: 10000,
      selectors: {
        mainContent: 'article, main, .content, .markdown-body, .docs-content, .documentation',
        title: 'h1, title',
        codeBlocks: 'pre code, .highlight code, pre'
      },
      ...config
    };

    this.turndownService = new TurndownService({
      codeBlockStyle: 'fenced',
      headingStyle: 'atx'
    });

    this.limit = pLimit(this.config.concurrency!);
  }

  /**
   * 开始爬取
   */
  async crawl(onProgress?: (progress: CrawlProgress) => void): Promise<CrawlResult> {
    console.log(`🚀 开始爬取: ${this.config.baseUrl}`);
    console.log(`📊 配置: 最大页数=${this.config.maxPages}, 并发=${this.config.concurrency}`);

    this.urlQueue.push(this.config.baseUrl);
    this.startTime = Date.now();

    while (this.urlQueue.length > 0 && this.crawledPages.length < this.config.maxPages!) {
      const batch = this.urlQueue.splice(0, this.config.concurrency!);
      
      const promises = batch.map(url => 
        this.limit(() => this.crawlPage(url))
      );

      await Promise.allSettled(promises);

      // 进度回调
      if (onProgress) {
        const elapsed = Date.now() - this.startTime;
        const speed = this.crawledPages.length / (elapsed / 1000);
        onProgress({
          current: this.crawledPages.length,
          total: this.config.maxPages!,
          queue: this.urlQueue.length,
          elapsed,
          speed
        });
      }

      // 速率限制
      if (this.config.rateLimit) {
        await this.sleep(this.config.rateLimit);
      }
    }

    const result = {
      pages: this.crawledPages,
      totalPages: this.crawledPages.length,
      duration: Date.now() - this.startTime,
      categories: this.categorizePages()
    };

    console.log(`✅ 爬取完成: ${result.totalPages} 页, 用时 ${this.formatDuration(result.duration)}`);
    return result;
  }

  /**
   * 爬取单个页面
   */
  protected async crawlPage(url: string): Promise<void> {
    if (this.visitedUrls.has(url)) return;
    this.visitedUrls.add(url);

    try {
      console.log(`📄 爬取: ${url}`);
      
      const response = await axios.get(url, {
        timeout: this.config.timeout,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; ArticleWriter-Crawler/1.0)'
        }
      });

      const $ = cheerio.load(response.data);
      
      // 提取内容
      const title = this.extractTitle($ as any);
      const content = this.extractMainContent($ as any);
      const codeExamples = this.extractCodeExamples($ as any);
      const links = this.extractLinks($ as any, url);

      const page: CrawledPage = {
        url,
        title,
        content,
        htmlContent: response.data,
        codeExamples,
        category: this.inferCategory(url, title),
        scrapedAt: new Date().toISOString(),
        links
      };

      this.crawledPages.push(page);

      // 将新链接加入队列
      this.addLinksToQueue(links);

    } catch (error: any) {
      console.error(`❌ 爬取失败 ${url}: ${error.message}`);
    }
  }

  /**
   * 提取标题
   */
  protected extractTitle($: any): string {
    const selector = this.config.selectors!.title!;
    const selectors = selector.split(',').map(s => s.trim());

    for (const sel of selectors) {
      const title = $(sel).first().text().trim();
      if (title) return title;
    }

    return 'Untitled';
  }

  /**
   * 提取主要内容
   */
  protected extractMainContent($: any): string {
    const selector = this.config.selectors!.mainContent!;
    const selectors = selector.split(',').map(s => s.trim());

    for (const sel of selectors) {
      const element = $(sel).first();
      if (element.length > 0) {
        // 移除不需要的元素
        element.find('nav, .sidebar, .toc, script, style, .navigation, .breadcrumb').remove();
        
        // 转换为 Markdown
        const html = element.html() || '';
        const markdown = this.turndownService.turndown(html);
        
        if (markdown.trim().length > 100) {
          return markdown;
        }
      }
    }

    return '';
  }

  /**
   * 提取代码示例
   */
  protected extractCodeExamples($: any): CodeExample[] {
    const selector = this.config.selectors!.codeBlocks!;
    const examples: CodeExample[] = [];

    $(selector).each((_: any, element: any) => {
      const $code = $(element);
      const content = $code.text().trim();
      
      if (content.length === 0 || content.length > 5000) return;

      // 检测语言
      const language = this.detectLanguage($code);
      
      examples.push({
        language,
        content,
        lineCount: content.split('\n').length
      });
    });

    return examples.slice(0, 20); // 限制每页最多20个代码示例
  }

  /**
   * 检测代码语言
   */
  protected detectLanguage($code: any): string {
    // 从 class 中提取
    const className = $code.attr('class') || '';
    
    const langPatterns = [
      /language-(\w+)/,
      /lang-(\w+)/,
      /highlight-(\w+)/,
      /(\w+)-highlight/
    ];

    for (const pattern of langPatterns) {
      const match = className.match(pattern);
      if (match) return match[1];
    }

    // 从父元素查找
    const parent = $code.parent();
    const parentClass = parent.attr('class') || '';
    for (const pattern of langPatterns) {
      const match = parentClass.match(pattern);
      if (match) return match[1];
    }

    // 内容启发式检测
    const content = $code.text();
    if (content.includes('import ') && content.includes('from ')) return 'javascript';
    if (content.includes('export ') && content.includes('const ')) return 'javascript';
    if (content.includes('def ') && content.includes(':')) return 'python';
    if (content.includes('<?php')) return 'php';
    if (content.includes('public class')) return 'java';
    if (content.includes('func ') && content.includes('return')) return 'go';

    return 'text';
  }

  /**
   * 提取链接
   */
  protected extractLinks($: any, currentUrl: string): string[] {
    const links: string[] = [];
    const baseUrl = new URL(this.config.baseUrl);

    $('a[href]').each((_: any, element: any) => {
      const href = $(element).attr('href');
      if (!href) return;

      try {
        const absoluteUrl = new URL(href, currentUrl).href;
        const parsedUrl = new URL(absoluteUrl);
        
        // 移除 hash 和 query
        parsedUrl.hash = '';
        const cleanUrl = parsedUrl.href;
        
        // 只保留同域名链接
        if (parsedUrl.hostname === baseUrl.hostname) {
          links.push(cleanUrl);
        }
      } catch {
        // 忽略无效 URL
      }
    });

    return [...new Set(links)]; // 去重
  }

  /**
   * 将链接加入队列
   */
  protected addLinksToQueue(links: string[]): void {
    for (const link of links) {
      if (this.shouldCrawl(link) && this.crawledPages.length < this.config.maxPages!) {
        this.urlQueue.push(link);
      }
    }
  }

  /**
   * 判断是否应该爬取该链接
   */
  protected shouldCrawl(url: string): boolean {
    // 已访问过
    if (this.visitedUrls.has(url)) return false;
    
    // 已在队列中
    if (this.urlQueue.includes(url)) return false;

    // URL 模式匹配
    const { include, exclude } = this.config.urlPatterns || {};

    if (exclude) {
      for (const pattern of exclude) {
        if (url.includes(pattern)) return false;
      }
    }

    if (include && include.length > 0) {
      return include.some(pattern => url.includes(pattern));
    }

    return true;
  }

  /**
   * 推断分类
   */
  protected inferCategory(url: string, title: string): string {
    const categoryPatterns: Record<string, string[]> = {
      'getting-started': ['intro', 'getting-started', 'quickstart', 'installation', 'setup'],
      'guide': ['guide', 'tutorial', 'how-to', 'learn'],
      'api': ['api', 'reference', 'docs/api', '/api/'],
      'examples': ['example', 'demo', 'sample', 'playground'],
      'advanced': ['advanced', 'deep-dive', 'internals', 'optimization'],
      'migration': ['migration', 'upgrade', 'changelog', 'breaking']
    };

    const combined = `${url.toLowerCase()} ${title.toLowerCase()}`;

    for (const [category, patterns] of Object.entries(categoryPatterns)) {
      if (patterns.some(p => combined.includes(p))) {
        return category;
      }
    }

    return 'other';
  }

  /**
   * 分类统计
   */
  protected categorizePages(): Record<string, CrawledPage[]> {
    const categories: Record<string, CrawledPage[]> = {};

    for (const page of this.crawledPages) {
      if (!categories[page.category]) {
        categories[page.category] = [];
      }
      categories[page.category].push(page);
    }

    return categories;
  }

  /**
   * 保存结果
   */
  async saveResults(outputDir: string): Promise<void> {
    await fs.ensureDir(outputDir);

    // 保存原始数据
    const rawDir = path.join(outputDir, 'pages');
    await fs.ensureDir(rawDir);

    for (const [index, page] of this.crawledPages.entries()) {
      const filename = `${String(index + 1).padStart(3, '0')}-${this.slugify(page.title)}.json`;
      await fs.writeJSON(path.join(rawDir, filename), page, { spaces: 2 });
    }

    // 保存摘要
    const summary: CrawlSummary = {
      name: this.config.name,
      baseUrl: this.config.baseUrl,
      totalPages: this.crawledPages.length,
      categories: Object.fromEntries(
        Object.entries(this.categorizePages()).map(([cat, pages]) => [cat, pages.length])
      ),
      crawledAt: new Date().toISOString()
    };

    await fs.writeJSON(path.join(outputDir, 'summary.json'), summary, { spaces: 2 });

    console.log(`💾 保存完成: ${outputDir}`);
  }

  // 工具方法
  protected sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  protected slugify(text: string): string {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .substring(0, 50);
  }

  protected formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${seconds}s`;
  }
}

