import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import { exec } from 'child_process'; 

const py_build_plugin = () => ({
  name: 'builder-ssg',
  configureServer(server) {
    const build = () => {
      exec('python src/main.py', (err, stdout, stderr) => {
        if (err){
          console.error("Script failed to update: ", stderr);
          return;
        }
        console.log(stdout);
        server.ws.send({ type: 'full-reload', path: "*"});
      });
    };
    build();

    server.watcher.on('add', build);
    server.watcher.on('change', (file) =>{
      if (file.endsWith('.md') || file.endsWith('.yaml')){
        build();
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