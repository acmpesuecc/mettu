import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import { execSync } from 'child_process'; 
import os from 'os';

const pythonexecutable = `${os.homedir()}/virtenv/pullgit/bin/python`;

const py_build_plugin = () => {
  let ready = false;
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

        if (path.includes('/content/') || path.includes('/templates/') || path.includes('/assets/css/')) {
          if (event === 'change') {
            const buildTarget = path.includes('/templates/') ? null : path;
            build(buildTarget);
          } else if (event === 'add' || event === 'unlink') {
            build();
          }
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