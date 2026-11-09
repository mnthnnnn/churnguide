#!/bin/bash
# ==============================================================================
# ChurnGuide: AI Customer Analytics & Churn Prediction System
# One-Click Double-Clickable Launcher for macOS
# ==============================================================================

# Ensure script runs from its own directory regardless of how Finder launches it
cd "$(cd "$(dirname "$0")" && pwd)"
echo "======================================================================"
echo "         AI Customer Analytics & Churn Prediction System"
echo "                     macOS One-Click Launcher"
echo "======================================================================"
echo "Working directory: $(pwd)"
echo ""

# Prevent matplotlib font-cache delay or permission warning
export MPLCONFIGDIR="${TMPDIR:-/tmp}/matplotlib_churnguide"
mkdir -p "$MPLCONFIGDIR" 2>/dev/null

# 1. Locate working Python 3.10+
SYSTEM_PYTHON=""

# Search common macOS Python paths (Apple Silicon, Homebrew, Official Python.org, system)
for py_candidate in \
    "python3" \
    "/opt/homebrew/bin/python3" \
    "/usr/local/bin/python3" \
    "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3" \
    "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3" \
    "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3" \
    "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3" \
    "python"
do
    if command -v "$py_candidate" >/dev/null 2>&1; then
        # Check if version >= 3.10
        ver_check=$("$py_candidate" -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)" 2>/dev/null)
        if [ "$ver_check" = "1" ]; then
            SYSTEM_PYTHON="$py_candidate"
            break
        fi
    fi
done

# 2. If Python is not found, offer automated zero-friction installation for Mac
if [ -z "$SYSTEM_PYTHON" ]; then
    echo "[INFO] Python 3.10+ was not detected on this Mac."
    echo "[INFO] Attempting automated setup..."
    echo ""

    if command -v brew >/dev/null 2>&1; then
        echo "[INFO] Homebrew detected. Installing Python 3.12 via Homebrew..."
        brew install python@3.12
        SYSTEM_PYTHON="python3"
    else
        echo "[INFO] Downloading official Python 3.12 installer for macOS from python.org..."
        PKG_FILE="/tmp/python-3.12.3-macos11.pkg"
        curl -L -o "$PKG_FILE" "https://www.python.org/ftp/python/3.12.3/python-3.12.3-macos11.pkg"
        
        if [ -f "$PKG_FILE" ]; then
            echo "[INFO] Launching macOS Python package installer..."
            open "$PKG_FILE"
            echo ""
            echo "Please complete the Python installer window that just opened."
            echo "Once installed, press ENTER here to continue..."
            read -r
            rm -f "$PKG_FILE"
            SYSTEM_PYTHON="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
        fi
    fi
fi

if [ -z "$SYSTEM_PYTHON" ] || ! command -v "$SYSTEM_PYTHON" >/dev/null 2>&1; then
    echo "[ERROR] Python 3.10 or newer is required to run ChurnGuide."
    echo "Please download and install Python from: https://www.python.org/downloads/"
    echo ""
    echo "Press ENTER to exit..."
    read -r
    exit 1
fi

PY_VERSION=$("$SYSTEM_PYTHON" --version 2>&1)
echo "[OK] Detected: $PY_VERSION ($SYSTEM_PYTHON)"
echo ""

# 3. Setup Virtual Environment (Detect if Windows venv exists and rebuild cleanly for macOS)
VENV_DIR=".venv"
VENV_PYTHON="$VENV_DIR/bin/python"

if [ -d "$VENV_DIR" ]; then
    # Check if this .venv has unix bin/python or if it's a Windows .venv with Scripts/
    if [ ! -f "$VENV_PYTHON" ]; then
        echo "[INFO] Existing .venv was created for Windows. Creating clean macOS virtual environment..."
        rm -rf "$VENV_DIR"
    else
        # Verify it runs
        if ! "$VENV_PYTHON" -c "import sys" >/dev/null 2>&1; then
            echo "[WARNING] Virtual environment invalid for this system. Rebuilding..."
            rm -rf "$VENV_DIR"
        fi
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating isolated virtual environment in .venv..."
    "$SYSTEM_PYTHON" -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "[WARNING] Could not create virtual environment. Falling back to host Python..."
        VENV_PYTHON="$SYSTEM_PYTHON"
    else
        echo "[OK] macOS virtual environment created successfully."
    fi
else
    echo "[OK] Virtual environment verified for macOS."
fi
echo ""

# 4. Verify runtime dependencies (Fast instant check via marker)
INSTALL_MARKER="$VENV_DIR/.installed_ok"
if [ ! -f "$INSTALL_MARKER" ]; then
    echo "[INFO] First-time setup: Checking runtime dependencies..."
    if ! "$VENV_PYTHON" -c "import pandas, flask, sklearn, matplotlib, joblib" >/dev/null 2>&1; then
        echo "[INFO] Installing required packages from requirements.txt..."
        "$VENV_PYTHON" -m pip install --upgrade pip >/dev/null 2>&1
        "$VENV_PYTHON" -m pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to install dependencies from requirements.txt."
            echo "Please check your internet connection and try again."
            echo "Press ENTER to exit..."
            read -r
            exit 1
        fi
    fi
    touch "$INSTALL_MARKER"
    echo "[OK] Runtime dependencies installed and verified."
else
    echo "[OK] Runtime dependencies verified (Instant launch mode)."
fi
echo ""

# 5. Verify pre-trained demo models
if [ ! -f "projects/telecom_public_demo/pipeline.joblib" ]; then
    echo "[INFO] Initializing pre-trained benchmark models..."
    "$VENV_PYTHON" scripts/initialize_demo_projects.py
    if [ $? -ne 0 ]; then
        echo "[ERROR] Model initialization failed."
        echo "Press ENTER to exit..."
        read -r
        exit 1
    fi
    echo "[OK] Benchmark models initialized successfully."
else
    echo "[OK] Pre-trained benchmark models verified."
fi
echo ""

# 6. Launch web server and browser
echo "======================================================================"
echo "Starting ChurnGuide production server at http://127.0.0.1:5000 ..."
echo "Your default browser will open automatically in a few seconds."
echo "Press Ctrl+C in this terminal window to stop the server anytime."
echo "======================================================================"
echo ""

"$VENV_PYTHON" app.py

