import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import { exec } from 'child_process'; 
import os from 'os';

const py_build_plugin = () => ({
  name: 'builder-ssg',
  configureServer(server) {
    const build = (file = null) => {
      console.log("start build process")
      const pythonexecutable = `${os.homedir()}/virtenv/pullgit/bin/python`;
      const command = file
      ?  `${pythonexecutable} src/main.py --file ${file}`
      :  `${pythonexecutable} src/main.py`;

      exec(command, (err, stdout, stderr) => {
        if (err){
          console.error("Script failed to update: ", stderr);
          return;
        }
        console.log(stdout);
        setTimeout(() => {
          server.ws.send({ type: 'full-reload', path: "*" });
          }, 100);
      });
    };
    build();

    server.watcher.on('add', build);
    server.watcher.on('change', (file) => {
      console.log(file)
      if (file.includes('content/') || file.includes('templates/')) {
        console.log("entered if")
        const buildTarget = file.includes('templates/') ? null : file;
        build(buildTarget);
      }
    });
    server.watcher.on('unlink', build);
  },
});


export default defineConfig({
  plugins: [
    py_build_plugin(),
    tailwindcss(),
  ],
  build: {
    outDir: './dist',
  },
});