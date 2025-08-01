import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import { exec, execSync } from 'child_process'; 
import os from 'os';

const pythonexecutable = `${os.homedir()}/virtenv/pullgit/bin/python`;

const py_build_plugin = () => {

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

        exec(command, (err, stdout, stderr) => {
          if (err) {
            console.error("Script failed to update: ", stderr);
            return;
          }
          console.log(stdout.trim());
          setTimeout(() => {
            server.ws.send({ type: 'full-reload', path: "*" });
          }, 100);
        });
      };

      build();

      server.watcher.on('change', (file) => {
        if (file.includes('/content/') || file.includes('/templates/')) {
          const buildTarget = file.includes('/templates/') ? null : file;
          build(buildTarget);
        }
      });

      server.watcher.on('add', () => build());
      server.watcher.on('unlink', () => build());
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