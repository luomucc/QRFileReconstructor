#!/bin/bash
# 初始化 Git 仓库并推送到 GitHub
echo "🔧 初始化 Git 仓库..."
git init
# 设置用户名和邮箱
git config user.name "AI Developer"
git config user.email "ai@aipyaipy.com"
# 添加所有文件
echo "📦 添加文件到暂存区..."
git add .
# 首次提交
echo "💾 提交初始代码..."
git commit -m "Initial commit: QR File Reconstructor"
# 添加远程仓库
echo "🌐 添加远程仓库: https://github.com/luomucc/QRFileReconstructor.git"
git remote add origin https://github.com/luomucc/QRFileReconstructor.git
# 推送到 main 分支
echo "🚀 推送到 GitHub main 分支..."
git branch -M main
git push -u origin main
echo "✅ 推送完成！"