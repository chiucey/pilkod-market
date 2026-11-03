#!/usr/bin/env bun
/**
 * Merge Comic Pages to PDF
 *
 * This script merges all comic page images (PNG format) into a single PDF file.
 * Each image becomes a full page in the PDF.
 *
 * Usage:
 *   bun merge-to-pdf.ts <comic-directory>
 *
 * Example:
 *   bun merge-to-pdf.ts comic/alan-turing-bio
 *
 * Requirements:
 *   - gm (GraphicsMagick) or imagemagick
 *   - Install: brew install graphicsmagick
 *
 * Note: This script should be called from the skill's scripts/ directory.
 * The comic-directory path should be an absolute or relative path from current working directory.
 */

import { mkdir, readdir, readFile } from "fs/promises";
import { join } from "path";
import { existsSync } from "fs";
import { execSync } from "child_process";

interface ComicDirectory {
  path: string;
  images: string[];
  title: string;
}

/**
 * Get all comic page images from directory
 * Expects naming format: NN-{cover|page}-{slug}.png
 */
async function getComicImages(dir: string): Promise<string[]> {
  const files = await readdir(dir);
  const images = files
    .filter((f) => f.endsWith(".png"))
    .filter((f) => /^\d{2}-(cover|page)-.+\.png$/.test(f))
    .sort(); // Sort alphabetically (01, 02, 03, etc.)

  return images;
}

/**
 * Extract title from directory name or analysis.md
 */
async function getComicTitle(dir: string): Promise<string> {
  const analysisPath = join(dir, "analysis.md");

  if (existsSync(analysisPath)) {
    const content = await readFile(analysisPath, "utf-8");
    const match = content.match(/^title:\s*"(.+)"$/m);
    if (match) {
      return match[1];
    }
  }

  // Fallback to directory name
  return dir.split("/").pop() || "comic";
}

/**
 * Merge images into PDF using GraphicsMagick
 */
function mergeToPDF(images: string[], outputPath: string, comicDir: string): void {
  const imagePaths = images.map((img) => join(comicDir, img)).join(" ");

  try {
    // Use GraphicsMagick's convert command
    const command = `gm convert ${imagePaths} "${outputPath}"`;
    console.log(`Executing: ${command}`);
    execSync(command, { stdio: "inherit" });
  } catch (error) {
    // Fallback to ImageMagick if GM fails
    try {
      const command = `convert ${imagePaths} "${outputPath}"`;
      console.log(`GraphicsMagick not found, trying ImageMagick...`);
      console.log(`Executing: ${command}`);
      execSync(command, { stdio: "inherit" });
    } catch (imError) {
      console.error("Error: Neither GraphicsMagick nor ImageMagick found.");
      console.error("Install with: brew install graphicsmagick");
      throw error;
    }
  }
}

/**
 * Main function
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error("Usage: bun merge-to-pdf.ts <comic-directory>");
    console.error("Example: bun merge-to-pdf.ts comic/alan-turing-bio");
    process.exit(1);
  }

  const comicDir = args[0];

  if (!existsSync(comicDir)) {
    console.error(`Error: Directory not found: ${comicDir}`);
    process.exit(1);
  }

  console.log(`\n📚 Merging comic pages to PDF...\n`);
  console.log(`📁 Source directory: ${comicDir}`);

  // Get comic images
  const images = await getComicImages(comicDir);

  if (images.length === 0) {
    console.error("Error: No comic page images found (expected format: NN-{cover|page}-{slug}.png)");
    process.exit(1);
  }

  console.log(`📄 Found ${images.length} page(s):`);
  images.forEach((img) => console.log(`   - ${img}`));

  // Get comic title
  const title = await getComicTitle(comicDir);
  console.log(`📖 Title: ${title}`);

  // Output PDF path
  const dirName = comicDir.split("/").pop() || "comic";
  const outputPath = join(comicDir, `${dirName}.pdf`);

  console.log(`\n🖼️  Creating PDF: ${outputPath}`);

  // Merge images
  mergeToPDF(images, outputPath, comicDir);

  console.log(`\n✅ PDF created successfully!`);
  console.log(`\n📍 Location: ${outputPath}`);
}

// Run
main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
