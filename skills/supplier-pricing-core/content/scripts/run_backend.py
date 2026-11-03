from pathlib import Path
import subprocess
import sys


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    vendor_backend = skill_root / "vendor" / "scripts" / "api_server.py"
    workspace_root = Path(__file__).resolve().parents[4]
    workspace_backend = workspace_root / "extracted_project" / "skills" / "taobao" / "scripts" / "api_server.py"

    if vendor_backend.exists():
        backend_script = vendor_backend
        print("Using portable vendor backend")
    elif workspace_backend.exists():
        backend_script = workspace_backend
        print("Vendor backend not found, fallback to workspace backend")
    else:
        print("ERROR: no backend script found in vendor or workspace path")
        return 1

    print(f"Starting backend: {backend_script}")
    proc = subprocess.run([sys.executable, str(backend_script)], cwd=str(backend_script.parent))
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())

