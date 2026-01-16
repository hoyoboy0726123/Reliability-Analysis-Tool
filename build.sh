#!/bin/bash
# Render.com 部署時的建置腳本
# 用於安裝系統依賴（中文字體）

echo "===== Installing Chinese fonts for PDF/Word generation ====="

# 更新套件列表
apt-get update

# 安裝中文字體
apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra fonts-wqy-zenhei fonts-wqy-microhei

# 更新字體緩存
fc-cache -fv

echo "===== Font installation completed ====="
echo "Available Chinese fonts:"
fc-list :lang=zh

# 安裝 Python 依賴
pip install -r requirements.txt

echo "===== Build completed ====="
