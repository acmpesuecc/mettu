import sharp from 'sharp';
import path from 'path';
import fs from 'fs-extra'; // Using fs-extra for ensureDirSync
import { fileURLToPath } from 'url';

// --- Configuration ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define the input and output directories relative to this script
const inputDir = path.resolve(__dirname, '../assets/images'); // Adjusted path assuming script is in 'src'
const outputDir = path.resolve(__dirname, '../assets/images-processed'); // Adjusted path

// Define the desired widths for responsive images
const widths = [400, 800, 1200];
const webpQuality = 80; // Quality setting for WebP images (0-100)

// --- Main Processing Function ---
export async function processImages(inDir, outDir) {
  console.log(`[images] Starting preprocessing from ${inDir} to ${outDir}`);

  try {
    // Ensure the output directory exists, create if it doesn't
    await fs.ensureDir(outDir);
    console.log(`[images] Output directory ensured: ${outDir}`);

    const files = await fs.readdir(inDir);
    console.log(`[images] Found ${files.length} items in input directory.`);

    for (const file of files) {
      const inputFile = path.join(inDir, file);
      const stats = await fs.stat(inputFile);

      // Skip directories and non-image files if necessary (basic check)
      if (stats.isDirectory() || !/\.(jpe?g|png|gif|tiff|webp|avif)$/i.test(file)) {
        console.log(`[images] Skipping: ${file} (Not a processable image)`);
        continue;
      }

      // Get filename without extension
      const baseName = path.parse(file).name;
      console.log(`[images] Processing: ${file}`);

      const imagePipeline = sharp(inputFile);

      // Generate different sizes
      for (const width of widths) {
        const outputFilename = `${baseName}-${width}w.webp`;
        const outputFile = path.join(outDir, outputFilename);

        try {
          await imagePipeline
            .clone() // Start fresh from the original for each size
            .resize({ width: width }) // Resize to target width
            .webp({ quality: webpQuality }) // Convert to WebP
            .toFile(outputFile); // Save the file

          console.log(`[images]   ✓ Generated: ${outputFilename}`);
        } catch (resizeError) {
          console.error(`[images]   ✗ Error generating ${width}w for ${file}:`, resizeError);
        }
      }
    }
    console.log('[images] Image preprocessing complete.');
  } catch (error) {
    console.error('[images] An error occurred during image processing setup:', error);
    // Optionally re-throw or exit if this is critical for the build
    // process.exit(1);
  }
}

// --- Allow running directly (optional, for testing) ---
// This part allows you to run `node src/image-preprocess.mjs` to test it.
// It might conflict if vite.config.mjs also calls processImages directly on import.
// Consider removing or commenting out this block if vite.config.mjs handles the initial call.
/*
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  processImages(inputDir, outputDir).catch(e => {
    console.error('[images] standalone processing failed', e);
    process.exit(1);
  });
}
*/