# mettu - a Static Site Generator using Python and Vite

mettu (మెట్లు, /ˈmɛt.t̪u/) is a simple static site generator that uses Python for backend processing and Vite for frontend development, with Tailwind and DaisyUI for styling. It allows you to create static websites using markdown files.

## Why the name?
"mettu" is a Telugu word meaning a stair or step. It felt like a great name given that this project is a step towards building tools myself, and convieniently, a step towards making a site!

## Requirements
- Python 3.x
- Node.js and npm
- Vite
- Tailwind CSS and DaisyUI

## Setup
1. Clone the repository
2. Install the required dependencies
   ```bash
   pip install -r requirements.txt
   npm install -D vite tailwindcss daisyui @tailwindcss/vite postcss glob 
   ```
3. Create a `.env` file in the root directory and set the environment variables "PY_EXECUTABLE" and "PYGMENTIZE_THEME".
4. Edit the `config.yaml` file to set your site name, author, and navigation links.
5. Create markdown files in the `content` directory. Each file should start similarly to the given examples.
6. Templates and svg icons are located in the `templates` directory. You can customize them as needed.
7. Assets like css, images, etc are placed in the `assets` directory.
8. Run the development server
   ```bash
   npm run dev
   ```
9. Build the site for production
   ```bash
   npm run build
   ```