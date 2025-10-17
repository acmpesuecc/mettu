import sharp from 'sharp';
import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';

// Configuration: Pick one resolution and format
const TARGET_WIDTH = 1280; // Single resolution for all images
const TARGET_FORMAT = 'webp'; // Modern format with good compression
const QUALITY = 75; // Balance between quality and file size

/**
 * Process images by converting them to a single optimized format/resolution
 * and overwriting the originals in the input directory
 */
export async function processImages(inputDir, outputDir) {
    // We'll ignore outputDir and work directly in inputDir to overwrite originals
    const actualDir = inputDir;
    
    const entries = await fs.readdir(actualDir, { withFileTypes: true });
    const files = entries
        .filter(e => e.isFile() && /\.(png|jpe?g|gif)$/i.test(e.name))
        .map(e => e.name);

    if (files.length === 0) {
        console.log('[img] No images to process');
        return;
    }

    console.log(`[img] Processing ${files.length} images...`);
    let processed = 0;
    let skipped = 0;

    for (const file of files) {
        const inputPath = path.join(actualDir, file);
        const baseName = file.replace(/\.(png|jpe?g|gif)$/i, '');
        const outputFile = `${baseName}.${TARGET_FORMAT}`;
        const outputPath = path.join(actualDir, outputFile);

        // Skip if already processed (same name with target format)
        if (file.toLowerCase().endsWith(`.${TARGET_FORMAT}`)) {
            console.log(`[img] ⏭️  Skipping ${file} (already ${TARGET_FORMAT})`);
            skipped++;
            continue;
        }

        try {
            const meta = await sharp(inputPath).metadata();
            const origWidth = meta.width || TARGET_WIDTH;

            // Resize only if original is wider than target
            const resizeWidth = origWidth > TARGET_WIDTH ? TARGET_WIDTH : origWidth;

            // Process and save
            await sharp(inputPath)
                .resize({ width: resizeWidth, withoutEnlargement: true })
                .webp({ quality: QUALITY })
                .toFile(outputPath);

            // Delete original if it's a different file
            if (inputPath !== outputPath) {
                await fs.unlink(inputPath);
                console.log(`[img] ✅ ${file} -> ${outputFile} (${resizeWidth}px, replaced original)`);
            } else {
                console.log(`[img] ✅ ${file} optimized in-place (${resizeWidth}px)`);
            }
            
            processed++;
        } catch (e) {
            console.error(`[img] ❌ Failed to process ${file}: ${e.message}`);
        }
    }

    console.log(`[img] Done! Processed: ${processed}, Skipped: ${skipped}`);
    
    // Clean up manifest cache if it exists (no longer needed)
    try {
        const manifestPath = '.cache/image-manifest.json';
        if (fsSync.existsSync(manifestPath)) {
            fsSync.unlinkSync(manifestPath);
        }
    } catch (e) {
        // Ignore cleanup errors
    }
}
