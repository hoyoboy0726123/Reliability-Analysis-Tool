#!/bin/bash
# Render.com 部署時的建置腳本
# 用於安裝系統依賴（中文字體）

echo "============================================================"
echo "  Installing Chinese fonts for PDF/Word generation"
echo "============================================================"

# 更新套件列表
echo -e "\n[1/5] Updating package list..."
apt-get update -qq

# 安裝中文字體（多個包確保至少一個可用）
echo -e "\n[2/5] Installing Chinese font packages..."
apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-arphic-ukai \
    fonts-arphic-uming

# 更新字體緩存
echo -e "\n[3/5] Updating font cache..."
fc-cache -fv

# 列出安裝的中文字體
echo -e "\n[4/5] Checking installed Chinese fonts..."
echo "Fonts with Chinese support:"
fc-list :lang=zh-tw | head -10
fc-list :lang=zh-cn | head -10

# 顯示字體文件位置
echo -e "\nFont files in /usr/share/fonts:"
find /usr/share/fonts -name "*CJK*" -o -name "*wqy*" -o -name "*Noto*" | head -20

# 下載備用字體（如果系統字體不可用）
echo -e "\n[5/6] Downloading fallback fonts..."
bash download_fonts.sh || echo "⚠ Fallback font download skipped"

# 安裝 Python 依賴
echo -e "\n[6/6] Installing Python dependencies..."
pip install -r requirements.txt

echo -e "\n============================================================"
echo "  ✓ Build completed successfully!"
echo "============================================================"
