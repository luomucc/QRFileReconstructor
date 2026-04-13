"""
使用 Python 执行 Git 推送操作到 GitHub
"""
import subprocess
import sys
import os
def run_git_command(cmd, desc):
    """运行 Git 命令"""
    print(f"\n🔧 {desc}...")
    print(f"  Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout.strip():
                print(f"  ✅ {result.stdout.strip()}")
            return True
        else:
            print(f"  ⚠️ {result.stderr.strip()}")
            # 有些警告是正常的（比如已经存在远程仓库）
            if "already exists" in result.stderr or "origin" in result.stderr:
                return True
            return False
    except FileNotFoundError:
        print("  ❌ 错误：未找到 Git 命令，请确保已安装 Git 并添加到 PATH")
        return False
    except Exception as e:
        print(f"  ❌ 异常：{str(e)}")
        return False
def main():
    remote_url = "https://github.com/luomucc/QRFileReconstructor.git"
    print("=" * 60)
    print("🚀 开始推送到 GitHub")
    print(f"📍 远程仓库: {remote_url}")
    print("=" * 60)
    # 1. 检查是否已经是 Git 仓库
    if not os.path.exists(".git"):
        if not run_git_command(["git", "init"], "初始化 Git 仓库"):
            return False
    else:
        print("🔍 已经是 Git 仓库，跳过初始化")
    # 2. 设置用户信息
    run_git_command(["git", "config", "user.name", "luomucc"], "设置用户名")
    run_git_command(["git", "config", "user.email", "luomucc@users.noreply.github.com"], "设置邮箱")
    # 3. 添加所有文件
    if not run_git_command(["git", "add", "."], "添加所有文件到暂存区"):
        return False
    # 4. 检查是否有改动
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("\n✅ 没有文件改动，跳过提交")
    else:
        # 首次提交
        if not run_git_command(["git", "commit", "-m", "Initial commit: QR File Reconstructor - 二维码文件重组工具"], "提交代码"):
            return False
    # 5. 添加远程仓库
    # 先检查是否已存在
    result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
    if result.returncode != 0:
        if not run_git_command(["git", "remote", "add", "origin", remote_url], "添加远程仓库"):
            return False
    else:
        print("\n🔍 远程仓库 origin 已存在，更新 URL...")
        run_git_command(["git", "remote", "set-url", "origin", remote_url], "更新远程 URL")
    # 6. 重命名分支为 main
    run_git_command(["git", "branch", "-M", "main"], "重命名分支为 main")
    # 7. 推送到远程
    print("\n🚀 开始推送到 GitHub main 分支...")
    print("   这可能需要几分钟时间，请耐心等待...")
    if not run_git_command(["git", "push", "-u", "origin", "main"], "推送到 GitHub"):
        print("\n❌ 推送失败！可能的原因：")
        print("   1. 需要输入用户名和密码/令牌")
        print("   2. 网络连接问题")
        print("   3. 仓库不存在")
        print("")
        print("💡 建议手动在命令行执行:")
        print("   git push -u origin main")
        return False
    print("\n" + "=" * 60)
    print("✅ 推送成功！")
    print(f"🌐 查看仓库: https://github.com/luomucc/QRFileReconstructor")
    print("📱 GitHub Actions 会自动编译 APK")
    print("⏳ 等待几分钟后，您可以在 Actions 标签页下载编译好的 APK")
    print("=" * 60)
    return True
if __name__ == "__main__":
    success = main()
    utils.set_state(success=success, result="Git 推送完成" if success else "Git 推送失败")