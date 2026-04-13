"""
修复 GitHub Actions - 升级 upload-artifact 到 v4
"""
import os
import subprocess
def fix_github_actions():
    """修复 GitHub Actions 配置"""
    workflow_dir = ".github/workflows"
    os.makedirs(workflow_dir, exist_ok=True)
    
    # 使用最新的 v4 版本
    workflow_content = """name: Android Build
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
    - name: Build with Gradle
      run: |
        cd QRFileReconstructor
        chmod +x gradlew
        ./gradlew assembleDebug --no-daemon
    - name: Upload APK artifact
      uses: actions/upload-artifact@v4
      with:
        name: qr-file-reconstructor-apk
        path: QRFileReconstructor/app/build/outputs/apk/debug/*.apk
        if-no-files-found: warn
    - name: Build summary
      run: |
        echo "✅ APK 编译完成！"
        echo "📱 请在 Actions 页面下载生成的 APK 文件"
        echo "🌐 仓库地址: https://github.com/${{ github.repository }}"
"""
    
    workflow_file = os.path.join(workflow_dir, "android-build.yml")
    with open(workflow_file, "w", encoding="utf-8") as f:
        f.write(workflow_content)
    
    print(f"✅ 已升级 GitHub Actions 配置到 v4 版本")
    print(f"   文件路径: {workflow_file}")
    
    # 显示关键改动
    print("\n🔧 关键改动:")
    print("   - actions/checkout@v3 → v4")
    print("   - actions/setup-java@v3 → v4")
    print("   - actions/upload-artifact@v3 → v4 ✅ (修复弃用问题)")
    print("   - 添加 if-no-files-found: warn 参数")
    
    return workflow_file
def push_to_github():
    """推送到 GitHub"""
    print("\n" + "="*60)
    print("🚀 推送修复到 GitHub")
    print("="*60)
    
    # 添加文件
    subprocess.run(["git", "add", ".github/workflows/android-build.yml"], check=False)
    subprocess.run(["git", "add", "."], check=False)
    
    # 提交
    commit_msg = "Fix: Upgrade GitHub Actions to v4 (fix deprecated upload-artifact)"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ 提交成功: {commit_msg}")
        print(result.stdout.strip())
    else:
        print("⚠️ 提交信息:", result.stderr.strip())
        # 强制添加并提交
        subprocess.run(["git", "add", "-A"], check=False)
        subprocess.run(["git", "commit", "--allow-empty", "-m", commit_msg], check=False)
    
    # 推送
    print("\n📤 推送到 GitHub...")
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ 推送成功！")
        print(result.stdout.strip())
        
        print("\n" + "="*60)
        print("🎉 修复完成！")
        print("🌐 仓库地址: https://github.com/luomucc/QRFileReconstructor")
        print("⚙️ Actions 页面: https://github.com/luomucc/QRFileReconstructor/actions")
        print("⏳ GitHub Actions 会自动重新触发编译")
        print("📱 等待 2-5 分钟后下载 APK")
        print("="*60)
        return True
    else:
        print("❌ 推送失败:")
        print(result.stderr)
        return False
def main():
    print("🔧 修复 GitHub Actions 弃用问题...")
    print("问题: actions/upload-artifact@v3 已弃用")
    print("解决方案: 升级到 v4 版本\n")
    
    # 1. 修复配置文件
    fix_github_actions()
    
    # 2. 推送到 GitHub
    success = push_to_github()
    
    if success:
        print("\n✅ 修复成功！请访问 Actions 页面查看新的编译任务。")
    else:
        print("\n⚠️ 推送失败，请手动执行:")
        print("   git add .")
        print("   git commit -m 'Fix: Upgrade GitHub Actions to v4'")
        print("   git push origin main")
    
    return success
if __name__ == "__main__":
    success = main()
    utils.set_state(success=success, result="GitHub Actions v4 升级完成" if success else "升级失败")