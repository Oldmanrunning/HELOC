# create_venv.py
"""
Create a virtual environment and install packages into it.

Usage examples:
  # default: create .venv and install 'markdown'
  py create_venv.py

  # custom venv path and packages
  py create_venv.py --path myenv --packages markdown streamlit fpdf

  # create venv and write requirements.txt
  py create_venv.py --write-reqs
"""

import argparse
import sys
import venv
import subprocess
from pathlib import Path
import shutil

def run(cmd, check=True):
    print(">", " ".join(map(str, cmd)))
    completed = subprocess.run(cmd)
    if check and completed.returncode != 0:
        raise SystemExit(f"Command failed (exit {completed.returncode}): {' '.join(map(str, cmd))}")
    return completed.returncode

def main():
    parser = argparse.ArgumentParser(description="Create a venv and install packages")
    parser.add_argument("--path", "-p", default=".venv", help="Path to create virtual environment (default: .venv)")
    parser.add_argument("--packages", "-k", nargs="*", default=["markdown"], help="Packages to install (default: markdown)")
    parser.add_argument("--python-exe", help="Optional: explicit python executable to use to create venv")
    parser.add_argument("--write-reqs", action="store_true", help="Write a requirements.txt alongside the venv")
    args = parser.parse_args()

    venv_path = Path(args.path).resolve()

    if args.python_exe:
        py_exe_for_venv = Path(args.python_exe).resolve()
    else:
        py_exe_for_venv = Path(sys.executable).resolve()

    print(f"Using Python to create venv: {py_exe_for_venv}")
    print(f"Target venv path: {venv_path}")

    # Create venv if not exists
    if venv_path.exists():
        print(f"Virtual environment already exists at {venv_path} — continuing to install packages into it.")
    else:
        print("Creating virtual environment...")
        # Use the stdlib venv module (uses current Python)
        venv_builder = venv.EnvBuilder(with_pip=True)
        venv_builder.create(str(venv_path))
        print("Virtual environment created.")

    # Determine venv python executable
    if sys.platform.startswith("win"):
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"

    if not venv_python.exists():
        raise SystemExit(f"Could not find python executable in venv at {venv_python}. venv creation may have failed.")

    print(f"Using venv python: {venv_python}")

    # Upgrade pip first (recommended)
    print("Upgrading pip inside the venv...")
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])

    # Install requested packages
    if args.packages:
        print(f"Installing packages into venv: {args.packages}")
        run([str(venv_python), "-m", "pip", "install"] + args.packages)
    else:
        print("No packages specified to install.")

    # Optionally write requirements.txt
    if args.write_reqs:
        reqs_path = Path("requirements.txt")
        print(f"Writing requirements file to {reqs_path}")
        # Freeze only the installed packages from this venv
        with reqs_path.open("wb") as f:
            subprocess.check_call([str(venv_python), "-m", "pip", "freeze"], stdout=f)
        print("requirements.txt written.")

    # Print quick verification/calls
    print("\n=== Done ===\n")
    print("Verify package is importable using the venv python:")
    print(f'  {venv_python} -c "import markdown; print(markdown.__version__)"')
    print("\nTo activate the venv (Windows CMD):")
    print(f'  {venv_path}\\Scripts\\activate')
    print("Or (PowerShell):")
    print(f'  {venv_path}\\Scripts\\Activate.ps1')
    print("\nTo run Streamlit without activating (recommended for automation):")
    print(f'  {venv_python} -m streamlit run heloc_streamlit_app.py')
    print("\nIf you prefer to activate, then run:")
    print("  streamlit run heloc_streamlit_app.py\n")

if __name__ == "__main__":
    main()
