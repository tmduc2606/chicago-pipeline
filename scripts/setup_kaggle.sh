#!/usr/bin/env bash
# scripts/setup_kaggle.sh — Verify and guide Kaggle API token setup
set -euo pipefail

KAGGLE_DIR="${HOME}/.kaggle"
KAGGLE_JSON="${KAGGLE_DIR}/kaggle.json"
KAGGLE_TOKEN="${KAGGLE_DIR}/access_token"

echo "=== Kaggle API Token Setup ==="
echo ""

# Check if either token format exists
json_exists=false
token_exists=false

if [ -f "$KAGGLE_JSON" ]; then
    json_exists=true
fi

if [ -f "$KAGGLE_TOKEN" ]; then
    token_exists=true
fi

if $json_exists || $token_exists; then
    if $json_exists; then
        echo "[OK] Kaggle token found at: $KAGGLE_JSON"
        chmod 600 "$KAGGLE_JSON" 2>/dev/null || true
    fi
    if $token_exists; then
        echo "[OK] Kaggle access_token found at: $KAGGLE_TOKEN"
        chmod 600 "$KAGGLE_TOKEN" 2>/dev/null || true
    fi

    # Verify token works
    if command -v kaggle &>/dev/null; then
        echo ""
        echo "Verifying API connection..."
        if kaggle datasets list -s "chicago-crime" --max-size 1 2>/dev/null | head -1; then
            echo "[OK] Kaggle API connection verified"
        else
            echo "[WARN] Token exists but API call failed"
        fi
    else
        echo ""
        echo "[WARN] kaggle CLI not installed"
        echo "       Install: pip install kaggle"
    fi
else
    echo "[MISSING] No Kaggle token found"
    echo ""
    echo "Option 1: KGAT Token (recommended)"
    echo "  1. Go to https://www.kaggle.com/settings"
    echo "  2. Under API, click 'Create New Token'"
    echo "  3. Run this command with your KGAT token:"
    echo ""
    echo "     mkdir -p $KAGGLE_DIR"
    echo "     echo YOUR_KGAT_TOKEN > $KAGGLE_TOKEN"
    echo "     chmod 600 $KAGGLE_TOKEN"
    echo ""
    echo "Option 2: JSON Token"
    echo "  1. Go to https://www.kaggle.com/settings"
    echo "  2. Under API, click 'Create New Token'"
    echo "  3. Move kaggle.json to: $KAGGLE_DIR"
    echo ""
    exit 1
fi

echo ""
echo "Ready for: make seed"
