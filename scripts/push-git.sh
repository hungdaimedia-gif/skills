#!/bin/bash
set -e

REPO_DIR="/Users/macos/Projects/skills"

echo "📂 Chuyển tới thư mục dự án: $REPO_DIR"
cd "$REPO_DIR"

echo "🔍 Kiểm tra trạng thái Git..."
git status --short

echo "📦 Đang thêm các file thay đổi..."
git add .

if git diff-index --quiet HEAD --; then
    echo "✨ Không có thay đổi mới nào để commit."
    echo "🚀 Kiểm tra đồng bộ với GitHub..."
    git push origin main
    echo "✅ Đã đồng bộ mới nhất với GitHub (Everything up-to-date)!"
else
    MSG="${1:-update: $(date '+%Y-%m-%d %H:%M:%S')}"
    echo "💾 Đang commit: $MSG"
    git commit -m "$MSG"
    echo "🚀 Đang push lên GitHub..."
    git push origin main
    echo "🎉 Cập nhật thành công lên GitHub!"
fi
