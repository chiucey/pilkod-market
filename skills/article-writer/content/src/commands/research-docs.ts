/**
 * 文档爬取命令 - CLI 接口
 */

import { CrawlerManager } from '../crawler/crawler-manager.js';
import type { CrawlOptions } from '../crawler/crawler-manager.js';
import { isDocumentationSite } from '../crawler/utils.js';
import { getPresetConfig, mergeConfig, validateConfig } from '../crawler/config.js';
import path from 'path';
import fs from 'fs-extra';

export interface ResearchDocsOptions {
  name: string;
  url?: string;
  pdf?: string;
  output?: string;
  dynamic?: boolean;
  maxPages?: number;
  concurrency?: number;
  preset?: string;
}

export class ResearchDocsCommand {
  /**
   * 执行文档爬取
   */
  async execute(options: ResearchDocsOptions): Promise<void> {
    try {
      // 验证参数
      this.validateOptions(options);

      // 确定输出目录
      const outputDir = options.output || path.join(process.cwd(), '_knowledge_base');
      await fs.ensureDir(outputDir);

      // 构建爬取选项
      const crawlOptions: CrawlOptions = {
        name: options.name,
        url: options.url,
        pdfPath: options.pdf,
        outputDir,
        useDynamic: options.dynamic,
        maxPages: options.maxPages,
        concurrency: options.concurrency
      };

      // 如果使用预设配置
      if (options.preset) {
        const preset = getPresetConfig(options.preset);
        if (preset) {
          console.log(`📦 使用预设配置: ${options.preset}`);
          if (preset.maxPages) crawlOptions.maxPages = preset.maxPages;
          if (preset.baseUrl && !crawlOptions.url) crawlOptions.url = preset.baseUrl;
        } else {
          console.warn(`⚠️  未找到预设配置: ${options.preset}`);
        }
      }

      // 自动检测是否需要动态爬取
      if (options.url && !options.dynamic) {
        if (CrawlerManager.isDynamicSite(options.url)) {
          console.log(`💡 检测到可能是动态网站，建议使用 --dynamic 参数`);
        }
      }

      // 执行爬取
      const manager = new CrawlerManager();
      const result = await manager.executeCrawl(crawlOptions);

      if (result) {
        console.log(`\n🎉 文档爬取成功!`);
        process.exit(0);
      } else {
        console.error(`\n❌ 文档爬取失败`);
        process.exit(1);
      }

    } catch (error: any) {
      console.error(`\n❌ 错误: ${error.message}`);
      if (error.stack) {
        console.error(error.stack);
      }
      process.exit(1);
    }
  }

  /**
   * 验证选项
   */
  private validateOptions(options: ResearchDocsOptions): void {
    if (!options.name) {
      throw new Error('必须提供项目名称 (--name)');
    }

    if (!options.url && !options.pdf) {
      throw new Error('必须提供 URL (--url) 或 PDF 文件路径 (--pdf)');
    }

    if (options.url && options.pdf) {
      throw new Error('不能同时提供 URL 和 PDF 文件路径');
    }

    if (options.pdf && !fs.existsSync(options.pdf)) {
      throw new Error(`PDF 文件不存在: ${options.pdf}`);
    }

    if (options.url) {
      try {
        new URL(options.url);
      } catch {
        throw new Error(`无效的 URL: ${options.url}`);
      }
    }
  }
}

/**
 * 导出便捷函数
 */
export async function researchDocs(options: ResearchDocsOptions): Promise<void> {
  const command = new ResearchDocsCommand();
  await command.execute(options);
}

