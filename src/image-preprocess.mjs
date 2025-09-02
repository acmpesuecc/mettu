import sharp from 'sharp';
import fs from 'fs/promises';
import path from 'path';

export async function processImages(inputDir, outputDir) {
    await fs.mkdir(outputDir, { recursive: true });
    const entries = await fs.readdir(inputDir, { withFileTypes: true });
    const files = entries
        .filter(entry => entry.isFile() && /\.(png|jpe?g|gif)$/i.test(entry.name))
        .map(entry => entry.name);

    for (const file of files) {

    const inputPath = path.join(inputDir, file);
    const outName = file.replace(/\.(png|jpe?g|gif)$/i, '.webp');
    const outputPath = path.join(outputDir, outName);

    try {
      await sharp(inputPath).resize({ width: 800 }).toFile(outputPath);
      console.log(`[img] Processed ${file} -> ${outName}`);
    } catch (e) {
      console.error(`[img] Failed ${file}: ${e.message}`);
    }
  }
}
