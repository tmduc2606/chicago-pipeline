#!/usr/bin/env bash
# scripts/setup_kaggle.sh — Verify and guide Kaggle API token setup
set -euo pipefail

KAGGLE_JSON="${HOME}/.kaggle/kaggle.json"

echo "=== Kaggle API Token Setup ==="
echo ""

if [ -f "$KAGGLE_JSON" ]; then
    echo "[OK] Kaggle token found at: $KAGGLE_JSON"
    chmod 600 "$KAGGLE_JSON" 2>/dev/null || true
    echo "[OK] Permissions set to 600"

    # Verify token works
    if command -v kaggle &>/dev/null; then
        echo ""
        echo "Verifying API connection..."
        if kaggle datasets list -s "chicago-crime" --max-size 1 2>/dev/null | head -1; then
            echo "[OK] Kaggle API connection verified"
        else
            echo "[WARN] Token exists but API call failed — check kaggle.json contents"
            echo "       Expected format: {\"username\": \"...\", \"key\": \"...\"}"
        fi
    else
        echo ""
        echo "[WARN] kaggle CLI not installed"
        echo "       Install: pip install kaggle"
    fi
else
    echo "[MISSING] No Kaggle token found at: $KAGGLE_JSON"
    echo ""
    echo "Setup instructions:"
    echo "  1. Go to https://www.kaggle.com/settings"
    echo "  2. Under 'API' section, click 'Create New Token'"
    echo "  3. Save the downloaded kaggle.json file to:"
    echo "       $KAGGLE_JSON"
    echo ""
    echo "  Or manually create it:"
    echo "       mkdir -p ~/.kaggle"
    echo "       echo '{\"username\":\"YOUR_USERNAME\",\"key\":\"YOUR_KEY\"}' > $KAGGLE_JSON"
    echo "       chmod 600 $KAGGLE_JSON"
    echo ""
    echo "Windows users:"
    echo "  Place kaggle.json at: %USERPROFILE%\\.kaggle\\kaggle.json"
    echo ""
    exit 1
fi

echo ""
echo "Ready for: make seed"
