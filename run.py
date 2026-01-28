import subprocess
import os
import sys
import time

def run_services():
    # Ensure we are in the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    print(f"Shift-T Unified Launcher - Independent Windows")
    print(f"--------------------------------------------")
    print(f"Project Root: {project_root}")

    # Creation flags for new console window (Windows only)
    if os.name == 'nt':
        creation_flags = subprocess.CREATE_NEW_CONSOLE
    else:
        creation_flags = 0

    # 1. Start Backend in new window
    print("Launching Backend in new window...")
    subprocess.Popen(
        [sys.executable, "apps/api/main.py"],
        cwd=project_root,
        creationflags=creation_flags,
        env=os.environ.copy()
    )

    # 2. Start Frontend in new window
    print("Launching Frontend in new window...")
    # Use npm.cmd on Windows, npm on others
    npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
    
    # Run npm start/dev in a way that keeps window open if it crashes?
    # cmd /k keeps window open.
    if os.name == 'nt':
        cmd_args = ["cmd.exe", "/c", "start", "cmd.exe", "/k", npm_cmd, "run", "dev"]
        # On Windows, 'start' command handles the new window, 
        # but subprocess.CREATE_NEW_CONSOLE works better for direct executable calls.
        # However, for npm, it's a batch file.
        # Let's try direct Popen with creationflags first, it usually works for npm.cmd too.
        
        subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=os.path.join(project_root, "apps", "web"),
            creationflags=creation_flags,
            env=os.environ.copy()
        )
    else:
        # Linux/Mac fallback (not asked for but good practice)
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=os.path.join(project_root, "apps", "web"),
            env=os.environ.copy()
        )

    print("\nServices launched in separate windows.")
    print("You can close this launcher window now.")

if __name__ == "__main__":
    run_services()
    time.sleep(2) # Give a moment to read the message
