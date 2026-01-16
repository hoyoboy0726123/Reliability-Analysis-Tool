#!/bin/bash
# 下載開源中文字體作為備用方案
# 使用已知在 ReportLab 上工作良好的 Noto Sans SC 字體

FONTS_DIR="./fonts"
mkdir -p "$FONTS_DIR"

echo "============================================================"
echo "  Downloading Chinese fonts for PDF generation"
echo "============================================================"

# 字體文件列表（使用 Google Fonts 的靜態資源）
declare -A FONTS=(
    ["NotoSansSC-Regular.otf"]="https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
)

DOWNLOAD_SUCCESS=0

for FONT_NAME in "${!FONTS[@]}"; do
    FONT_URL="${FONTS[$FONT_NAME]}"
    FONT_FILE="$FONTS_DIR/$FONT_NAME"

    # 檢查字體是否已存在
    if [ -f "$FONT_FILE" ] && [ -s "$FONT_FILE" ]; then
        echo "✓ Font already exists: $FONT_NAME"
        DOWNLOAD_SUCCESS=1
        continue
    fi

    # 下載字體
    echo "Downloading $FONT_NAME..."

    if command -v curl &> /dev/null; then
        curl -L -o "$FONT_FILE" "$FONT_URL" 2>/dev/null
    elif command -v wget &> /dev/null; then
        wget -q -O "$FONT_FILE" "$FONT_URL" 2>/dev/null
    else
        echo "⚠ Neither curl nor wget found"
        continue
    fi

    # 驗證下載
    if [ -f "$FONT_FILE" ] && [ -s "$FONT_FILE" ]; then
        FILE_SIZE=$(du -h "$FONT_FILE" | cut -f1)
        echo "✓ Downloaded: $FONT_NAME ($FILE_SIZE)"
        DOWNLOAD_SUCCESS=1
    else
        echo "✗ Failed to download: $FONT_NAME"
        rm -f "$FONT_FILE"
    fi
done

echo "============================================================"

if [ $DOWNLOAD_SUCCESS -eq 1 ]; then
    echo "✓ Font download completed"
    ls -lh "$FONTS_DIR"
    exit 0
else
    echo "⚠ No fonts were downloaded"
    exit 1
fi
