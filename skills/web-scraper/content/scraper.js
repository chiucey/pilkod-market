#!/usr/bin/env node

/**
 * Web Scraper Helper Script
 * 用于处理和保存网页爬取结果
 */

const fs = require('fs');
const path = require('path');

/**
 * 保存爬取结果到JSON文件
 * @param {Object} data - 爬取的数据
 * @param {string} outputPath - 输出文件路径
 */
function saveToJson(data, outputPath) {
    try {
        const dir = path.dirname(outputPath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
        fs.writeFileSync(outputPath, JSON.stringify(data, null, 2), 'utf-8');
        console.log(`Data saved to: ${outputPath}`);
        return true;
    } catch (error) {
        console.error(`Error saving data: ${error.message}`);
        return false;
    }
}

/**
 * 保存爬取结果到CSV文件
 * @param {Array} data - 爬取的数据数组
 * @param {string} outputPath - 输出文件路径
 */
function saveToCsv(data, outputPath) {
    try {
        if (!Array.isArray(data) || data.length === 0) {
            console.error('Data must be a non-empty array for CSV export');
            return false;
        }

        const dir = path.dirname(outputPath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        // 获取所有唯一的键
        const headers = [...new Set(data.flatMap(item => Object.keys(item)))];

        // 构建CSV内容
        let csvContent = headers.join(',') + '\n';

        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header] || '';
                // 转义引号和逗号
                const escaped = String(value).replace(/"/g, '""');
                return `"${escaped}"`;
            });
            csvContent += values.join(',') + '\n';
        });

        fs.writeFileSync(outputPath, csvContent, 'utf-8');
        console.log(`Data saved to CSV: ${outputPath}`);
        return true;
    } catch (error) {
        console.error(`Error saving CSV: ${error.message}`);
        return false;
    }
}

/**
 * 过滤和清洗文本
 * @param {string} text - 原始文本
 * @returns {string} - 清洗后的文本
 */
function cleanText(text) {
    if (!text) return '';

    return text
        .replace(/\s+/g, ' ')           // 合并多个空格
        .replace(/[\n\r\t]+/g, ' ')     // 替换换行和制表符
        .trim();
}

/**
 * 提取URL列表
 * @param {string} html - HTML内容
 * @param {string} baseUrl - 基础URL
 * @returns {Array} - URL列表
 */
function extractLinks(html, baseUrl) {
    const linkRegex = /<a[^>]+href=["']([^"']+)["'][^>]*>/gi;
    const links = [];
    let match;

    while ((match = linkRegex.exec(html)) !== null) {
        let url = match[1];

        // 处理相对URL
        if (url.startsWith('/')) {
            const parsed = new URL(baseUrl);
            url = `${parsed.origin}${url}`;
        } else if (!url.startsWith('http')) {
            url = new URL(url, baseUrl).href;
        }

        if (!links.includes(url)) {
            links.push(url);
        }
    }

    return links;
}

/**
 * 提取图片URL列表
 * @param {string} html - HTML内容
 * @returns {Array} - 图片URL列表
 */
function extractImages(html) {
    const imgRegex = /<img[^>]+src=["']([^"']+)["'][^>]*>/gi;
    const images = [];
    let match;

    while ((match = imgRegex.exec(html)) !== null) {
        images.push(match[1]);
    }

    return images;
}

// 导出模块
module.exports = {
    saveToJson,
    saveToCsv,
    cleanText,
    extractLinks,
    extractImages
};

// CLI入口
if (require.main === module) {
    const args = process.argv.slice(2);

    if (args.length < 2) {
        console.log('Usage:');
        console.log('  node scraper.js json <data> <output-path>');
        console.log('  node scraper.js csv <data-json> <output-path>');
        process.exit(1);
    }

    const command = args[0];
    const inputData = args[1];
    const outputPath = args[2];

    try {
        const data = JSON.parse(inputData);

        if (command === 'json') {
            saveToJson(data, outputPath);
        } else if (command === 'csv') {
            saveToCsv(Array.isArray(data) ? data : [data], outputPath);
        } else {
            console.error(`Unknown command: ${command}`);
            process.exit(1);
        }
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}
