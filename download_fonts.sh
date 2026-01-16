#!/bin/bash
# 下載開源中文字體作為備用方案
# 如果系統字體不可用，使用項目內嵌字體

FONTS_DIR="./fonts"
FONT_URL="https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
FONT_FILE="$FONTS_DIR/NotoSansCJKsc-Regular.otf"

echo "============================================================"
echo "  Downloading fallback Chinese font"
echo "============================================================"

# 創建字體目錄
mkdir -p "$FONTS_DIR"

# 檢查字體是否已存在
if [ -f "$FONT_FILE" ]; then
    echo "✓ Font already exists: $FONT_FILE"
    exit 0
fi

# 下載字體
echo "Downloading Noto Sans CJK SC..."
if command -v wget &> /dev/null; then
    wget -q -O "$FONT_FILE" "$FONT_URL"
elif command -v curl &> /dev/null; then
    curl -sL -o "$FONT_FILE" "$FONT_URL"
else
    echo "⚠ Neither wget nor curl found, skipping font download"
    exit 1
fi

# 驗證下載
if [ -f "$FONT_FILE" ] && [ -s "$FONT_FILE" ]; then
    echo "✓ Font downloaded successfully: $FONT_FILE"
    ls -lh "$FONT_FILE"
else
    echo "✗ Font download failed"
    exit 1
fi

echo "============================================================"
