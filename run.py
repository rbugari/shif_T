import subprocess
import time
import os
import sys
import webbrowser

def run_command(command, cwd=None, new_window=True):
    """Runs a command in a new terminal window or background depending on OS."""
    if sys.platform == "win32":
        # Windows-specific to open new cmd window
        if new_window:
            return subprocess.Popen(f"start cmd /k {command}", shell=True, cwd=cwd)
        else:
            return subprocess.Popen(command, shell=True, cwd=cwd)
    else:
        # Fallback for Linux/Mac (just runs in background for now)
        return subprocess.Popen(command, shell=True, cwd=cwd)

def main():
    print("🚀 Starting Shift-T (Release R1)...")
    base_dir = os.getcwd()
    
    # 1. Start Backend
    print("🔹 Launching Backend (FastAPI)...")
    backend_cmd = r".\.venv\Scripts\python apps\api\main.py"  # Using absolute path to python in venv
    run_command(backend_cmd, cwd=base_dir)
    
    # 2. Start Frontend
    print("🔹 Launching Frontend (Next.js)...")
    frontend_dir = os.path.join(base_dir, "apps", "web")
    # Using 'npm run dev' which often calls 'next dev'
    frontend_cmd = "npm run dev -- -p 3001" 
    run_command(frontend_cmd, cwd=frontend_dir)
    
    # 3. Wait and Open Browser
    print("⏳ Waiting for services to initialize...")
    time.sleep(5) # Give it a moment
    
    url = "http://localhost:3001"
    print(f"🌍 Opening {url}")
    webbrowser.open(url)
    
    print("\n✅ Shift-T is running!")
    print("Press Ctrl+C in the terminal windows to stop the servers.")

if __name__ == "__main__":
    main()
