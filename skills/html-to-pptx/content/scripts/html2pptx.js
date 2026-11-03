#!/usr/bin/env node
/**
 * HTML Slides → PPTX Converter
 * Uses pptxgenjs to convert HTML slide content to PowerPoint
 * Usage: node html2pptx.js "<title>" "<slide1_content>" "<slide2_content>" ...
 */
const PptxGenJS = require('/usr/local/lib/node_modules/pptxgenjs');
const fs = require('fs');

function htmlToPlainText(html) {
  return html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .trim();
}

function extractSlides(htmlContent) {
  // Split by horizontal rules or double newlines that look like slide separators
  const slideTexts = [];
  const parts = htmlContent.split(/<hr\s*\/?>/i);
  for (const part of parts) {
    const text = htmlToPlainText(part).trim();
    if (text) slideTexts.push(text);
  }
  return slideTexts.length > 0 ? slideTexts : [htmlToPlainText(htmlContent)];
}

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node html2pptx.js "<title>" "<slide1_content>" "<slide2_content>" ...');
  process.exit(1);
}

const title = args[0];
const slideContents = args.slice(1);

const pptx = new PptxGenJS();
pptx.title = title;
pptx.author = 'html-to-pptx skill';
pptx.subject = 'HTML Presentation';

// Parse slides
const slides = [];
for (const arg of slideContents) {
  const parsed = extractSlides(arg);
  slides.push(...parsed);
}

if (slides.length === 0) {
  slides.push(title);
}

// Create slides
slides.forEach((text, i) => {
  const slide = pptx.addSlide();
  slide.background = { color: 'FFFFFF' };

  // Title (first line) + content
  const lines = text.split('\n').filter(l => l.trim());
  if (lines.length === 0) return;

  const firstLine = lines[0];
  const restLines = lines.slice(1).join('\n');

  // Title
  slide.addText(firstLine, {
    x: 0.5,
    y: 0.3,
    w: '90%',
    h: 0.8,
    fontSize: 24,
    bold: true,
    color: '2D5F8A',
    fontFace: 'Arial'
  });

  // Content
  if (restLines) {
    slide.addText(restLines, {
      x: 0.5,
      y: 1.2,
      w: '90%',
      h: '80%',
      fontSize: 14,
      color: '333333',
      fontFace: 'Arial',
      valign: 'top',
      lineSpacingMultiple: 1.2
    });
  }

  // Slide number
  slide.addText(`${i + 1} / ${slides.length}`, {
    x: '90%',
    y: '95%',
    w: '1',
    h: 0.3,
    fontSize: 10,
    color: '999999',
    align: 'right'
  });
});

const outputPath = `/tmp/${title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.pptx`;
pptx.writeFile({ fileName: outputPath })
  .then(() => {
    console.log('SUCCESS: ' + outputPath);
  })
  .catch(err => {
    console.error('ERROR:', err.message);
    process.exit(1);
  });
