import os
import subprocess
import sys
def run_command(cmd, cwd=None):
    """运行命令并返回输出（忽略编码错误）"""
    try:
        # 使用二进制模式读取，然后尝试解码
        result = subprocess.run(cmd, cwd=cwd, shell=True, 
                              capture_output=True, timeout=300)
        
        # 尝试解码输出，忽略错误
        stdout = result.stdout.decode('utf-8', errors='ignore')
        stderr = result.stderr.decode('utf-8', errors='ignore')
        
        return result.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        return -1, "", "命令执行超时（5分钟）"
    except Exception as e:
        return -2, "", f"命令执行异常: {str(e)}"
def main():
    print("=" * 50)
    print("  二维码文件重组工具 - APK 编译脚本 (稳健版)")
    print("=" * 50)
    print()
    
    # 切换到项目目录
    project_dir = os.path.join(os.getcwd(), "QRFileReconstructor")
    if not os.path.exists(project_dir):
        print(f"❌ 错误：项目目录不存在: {project_dir}")
        print("请确保 QRFileReconstructor 文件夹存在。")
        return False
    
    print(f"📁 项目目录: {project_dir}")
    
    # 检查 gradlew.bat 是否存在
    gradlew_bat = os.path.join(project_dir, "gradlew.bat")
    if not os.path.exists(gradlew_bat):
        print(f"❌ 错误：gradlew.bat 不存在")
        return False
    
    # 1. 清理之前的构建
    print("\n1. 清理之前的构建...")
    returncode, stdout, stderr = run_command("gradlew.bat clean", cwd=project_dir)
    
    if returncode != 0:
        print(f"⚠️ 清理过程有警告 (代码: {returncode})")
        if stderr:
            print(f"   错误: {stderr[:100]}")
    else:
        print("✅ 清理完成")
    
    # 2. 编译 Debug APK
    print("\n2. 开始编译 Debug APK...")
    print("   这可能需要几分钟，请耐心等待...")
    
    returncode, stdout, stderr = run_command("gradlew.bat assembleDebug", cwd=project_dir)
    
    # 提取关键信息
    if "BUILD SUCCESSFUL" in stdout:
        print("✅ 编译成功！")
        success = True
    elif "BUILD FAILED" in stdout:
        print("❌ 编译失败")
        print(f"   错误摘要: {stderr[:200] if stderr else stdout[-500:]}")
        success = False
    else:
        print(f"⚠️ 编译状态未知 (返回码: {returncode})")
        success = returncode == 0
    
    # 3. 查找生成的 APK 文件
    print("\n3. 查找生成的 APK 文件...")
    
    # 可能的 APK 路径
    possible_paths = [
        os.path.join(project_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk"),
        os.path.join(project_dir, "app", "build", "outputs", "apk", "debug", "app-debug-aligned.apk"),
        os.path.join(project_dir, "app", "build", "outputs", "apk", "debug", "QRFileReconstructor-debug.apk"),
    ]
    
    apk_found = None
    for apk_path in possible_paths:
        if os.path.exists(apk_path):
            apk_found = apk_path
            break
    
    if apk_found:
        print(f"✅ APK 编译成功！")
        print(f"📱 APK 位置: {apk_found}")
        print(f"📏 文件大小: {os.path.getsize(apk_found) / 1024 / 1024:.2f} MB")
        print()
        print("🎯 安装指南:")
        print("   1. 将上面的 APK 文件复制到手机")
        print("   2. 在手机文件管理器中找到该文件")
        print("   3. 点击安装（可能需要允许'安装未知来源应用'）")
        print("   4. 安装完成后打开应用测试")
        
        # 复制 APK 到当前目录方便访问
        import shutil
        target_path = os.path.join(os.getcwd(), "qrfileresconstructor-debug.apk")
        shutil.copy2(apk_found, target_path)
        print(f"\n💾 已复制 APK 到: {target_path}")
        return True
    else:
        print("❌ 错误：APK 文件未找到")
        print("   尝试搜索所有 APK 文件...")
        
        apk_files = []
        for root, dirs, files in os.walk(os.path.join(project_dir, "app", "build")):
            for file in files:
                if file.endswith(".apk"):
                    full_path = os.path.join(root, file)
                    apk_files.append(full_path)
        
        if apk_files:
            print(f"   找到 {len(apk_files)} 个 APK 文件:")
            for apk in apk_files[:3]:  # 只显示前3个
                print(f"   - {apk}")
            # 使用第一个找到的 APK
            import shutil
            target_path = os.path.join(os.getcwd(), "qrfileresconstructor-debug.apk")
            shutil.copy2(apk_files[0], target_path)
            print(f"\n💾 已复制第一个 APK 到: {target_path}")
            return True
        else:
            print("   未找到任何 APK 文件")
            return False
if __name__ == "__main__":
    success = main()
    utils.set_state(success=success, result="APK编译完成" if success else "APK编译失败")