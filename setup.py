import os
import subprocess
import sys
import asyncio

async def c_u_file():
    env_path = '.env'
    if not os.path.exists(env_path):
        print('creating .env file')
    with open('.env','r+') as f:
        f.write("PYGMENTIZE_THEME")
        f.write("PY_EXECUTABLE")
    print('.env file has been made with default values')

async def npm_dependencies():
    try:
        subprocess.check_call(['npm','install','-D','vite','tailwindcss','daisyui','@tailwindcss/vite','postcss','glob'])
    except subprocess.CalledProcessError as e:
        print(f'Error Occurred: {e}')

async def pyth_dependenciesinstaller():
    if os.path.exists('requirements.txt'):
        print('Running pip install')
        try:
            subprocess.check_call([sys.executable, '-m','pip','install','-r','requirements.txt'])
        except subprocess.CalledProcessError as e:
            print(f'Error Occured while using pip install: {e}')
            os.exit()
    else:
        print("Requiremens.txt not found, check that you are in the correct directory")
async def venvChecker():
    if sys.prefix == sys.base.prefix:
        print("Virtual environment not detected")
    else:
            if os.path.exists('package.json'):
                print('JSON installer running')
                try:
                    subprocess.check_call(['npm','install'])
                except subprocess.CalledProcessError as e:
                    print(f'Error Occured: {e}')
                    os._exit()
            else:
                print('JSON file not present. Make sure you are in right directory')
async def run():
    print("Running 'npm run dev'")
    try:
        await asyncio.to_thread(subprocess.check_call, ['npm', 'run', 'dev'])
    except subprocess.CalledProcessError as e:
        print(f"Error while running server: {e}")
        sys.exit(1)
async def main():
    print("Starting the setup process...")

    await c_u_file()

    await venvChecker()

    await npm_dependencies()

    await pyth_dependenciesinstaller()

    await run()

if __name__ == "__main__":
    asyncio.run(main())