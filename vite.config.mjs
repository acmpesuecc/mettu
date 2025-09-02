import { defineConfig } from "vite";
import dotenv from 'dotenv';
import tailwindcss from "@tailwindcss/vite";
import { execSync } from 'child_process';
import os from 'os';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { processImages } from './src/image-preprocess.mjs';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const inputDir = path.join(__dirname, '/assets/images');
const outputDir = path.join(__dirname, '/assets/images-processed');

processImages(inputDir, outputDir).catch(e =>
  console.error('[images] initial processing failed', e)
);

const pythonexecutable = process.env.PY_EXECUTABLE;


const py_build_plugin = () => {
  let ready = false;

  const syntaxCssPath = './assets/css/syntax.css';
  if (!fs.existsSync(syntaxCssPath)) {
    console.log('Syntax CSS not found. Generating...');
    try {
      execSync(`pygmentize -S ${process.env.DAISYUI_THEME} -f html > ${syntaxCssPath}`);
      console.log('Generated syntax.css');
    } catch (e) {
      console.error('Failed to generate syntax.css. Make sure "pygmentize" is installed and in your PATH.', e);
    }
  }

  const handleExit = () => {
    console.log('\nCleaning up build files...');
    try {
      const output = execSync(`${pythonexecutable} src/main.py --clean`);
      console.log(output.toString().trim());
    } catch (e) {
      console.error("Cleanup script failed:", e);
    }
    process.exit();
  };

  process.on('SIGINT', handleExit);

  return {
    name: 'builder-ssg',
    configureServer(server) {
      const build = (file = null) => {
        const command = file
          ? `${pythonexecutable} src/main.py --file ${file}`
          : `${pythonexecutable} src/main.py`;

        try {
          const output = execSync(command);
          console.log(output.toString().trim());

          server.ws.send({ type: 'full-reload', path: "*" });
          ready = true;
        } catch (e) {
          console.error("Script failed to update: ", e);
        }
      };

      build();

      server.watcher.on('all', (event, path) => {
        if (!ready) {
          return;
        }

        if (path.includes('/content/') || path.includes('/templates/')) {
          if (event === 'change') {
            const buildTarget = path.includes('/templates/') ? null : path;
            build(buildTarget);
          } else if (event === 'add' || event === 'unlink') {
            build();
          }
        }
        if (event === 'change' && path.includes('/assets/css/')) {
          build();
        }
        if (event === 'unlink') { // if html files are deleted
          build();
        }
      });
    },
  };
};


export default defineConfig({
  plugins: [
    py_build_plugin(),
    tailwindcss(),
  ],
  build: {
    outDir: './dist',
  },
});