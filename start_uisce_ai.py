# start_uisce_ai.py
"""
Zero-setup launcher for Uisce-AI.
- Creates/uses .venv automatically
- Installs requirements.txt if present (first run only)
- Runs v2 by default; falls back to v1 if needed
"""

import os, sys, subprocess, venv, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(ROOT, ".venv")

def in_venv() -> bool:
    return sys.prefix != sys.base_prefix

def ensure_venv():
    if not os.path.exists(VENV_DIR):
        print("🔧 Creating virtual environment (.venv)...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)

def reexec_in_venv():
    # pick the python inside the venv
    py = os.path.join(VENV_DIR, "Scripts", "python.exe") if os.name == "nt" \
         else os.path.join(VENV_DIR, "bin", "python")
    if os.path.abspath(sys.executable) != os.path.abspath(py):
        # re-run this script inside the venv
        os.execv(py, [py, __file__])

def pip_install_if_needed():
    req = os.path.join(ROOT, "requirements.txt")
    if os.path.exists(req):
        # Simple heuristic: create a marker after successful install
        marker = os.path.join(VENV_DIR, ".deps_installed")
        if not os.path.exists(marker):
            print("📦 Installing dependencies from requirements.txt ...")
            rc = subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            rc |= subprocess.call([sys.executable, "-m", "pip", "install", "-r", req])
            if rc == 0:
                open(marker, "w").close()

def run_agent():
    # Prefer v2
    try:
        from uisce_ai_v2 import is_framework_agent_v2 as v2
        if hasattr(v2, "main"):
            return v2.main()
        # Fallback to module run if main not provided
        return subprocess.call([sys.executable, "-m", "uisce_ai_v2.is_framework_agent_v2"])
    except Exception as e:
        print("ℹ️ Could not start v2:", e)
        print("↩️ Falling back to v1 ...")
        import is_framework_agent as v1
        if hasattr(v1, "main"):
            return v1.main()
        return subprocess.call([sys.executable, os.path.join(ROOT, "is_framework_agent.py")])

if __name__ == "__main__":
    if not in_venv():
        ensure_venv()
        reexec_in_venv()
    pip_install_if_needed()
    sys.exit(run_agent())
