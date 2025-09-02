import sharp from 'sharp';
import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';


const TARGET_WIDTHS = [320, 640, 960, 1280, 1920];
const FORMATS = [
    { ext: 'webp', to: img => img.webp({ quality: 70 }) },
    { ext: 'avif', to: img => img.avif({ quality: 45 }) },
    { ext: 'jpg', to: img => img.jpeg({ quality: 80, mozjpeg: true, progressive: true }) },
];


export async function processImages(inputDir, outputDir) {
    await fs.mkdir(outputDir, { recursive: true });
    const entries = await fs.readdir(inputDir, { withFileTypes: true });
    const files = entries
        .filter(e => e.isFile() && /\.(png|jpe?g|gif)$/i.test(e.name))
        .map(e => e.name);

    const manifest = {}; // { originalFile: { format: [{ width, path }] } }

    for (const file of files) {
        const inputPath = path.join(inputDir, file);   // FIX
        let meta;
        try {
            meta = await sharp(inputPath).metadata();
        } catch (e) {
            console.error(`[img] metadata fail ${file}: ${e.message}`);
            continue;
        }

        const origWidth = meta.width || Math.max(...TARGET_WIDTHS);
        const widths = [...new Set(
            TARGET_WIDTHS.filter(w => w <= origWidth).concat([origWidth])
        )].sort((a, b) => a - b);

        const baseName = file.replace(/\.(png|jpe?g|gif)$/i, '');
        for (const w of widths) {
            for (const fmt of FORMATS) {
                const outFile = `${baseName}-${w}.${fmt.ext}`;
                const outPath = path.join(outputDir, outFile);
                try {
                    await fmt.to(sharp(inputPath).resize({ width: w })).toFile(outPath);
                    console.log(`[img] ${file} -> ${outFile}`);
                    (manifest[file] ||= {});
                    (manifest[file][fmt.ext] ||= []).push({
                        width: w,
                        path: path.posix.join(
                            path.relative(process.cwd(), outputDir).split(path.sep).join('/'),
                            outFile
                        )
                    });
                } catch (e) {
                    console.error(`[img] fail ${file} (${w}px ${fmt.ext}): ${e.message}`);
                }
            }
        }
        // Sort each format list by width ascending
        Object.values(manifest[file]).forEach(arr => arr.sort((a, b) => a.width - b.width));
    }

    fsSync.mkdirSync('.cache', { recursive: true });
    fsSync.writeFileSync('.cache/image-manifest.json', JSON.stringify(manifest, null, 2));
    return manifest;
}
