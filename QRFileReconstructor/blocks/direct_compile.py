import os
import subprocess
import shutil
def run_gradle_command(cmd):
    """运行 Gradle 命令"""
    print(f"  执行: {cmd}")
    
    try:
        # 使用 shell=True 确保正确执行 .bat 文件
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 收集输出
        output_lines = []
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                output_lines.append(line)
                # 显示关键进度信息
                if "> Task" in line or "BUILD" in line or "FAILED" in line or "SUCCESSFUL" in line:
                    print(f"    {line.strip()}")
        
        process.wait()
        output = "".join(output_lines)
        
        return process.returncode, output
        
    except Exception as e:
        return -1, f"命令执行异常: {str(e)}"
def main():
    print("=" * 60)
    print("       二维码文件重组工具 - APK 直接编译")
    print("=" * 60)
    print()
    
    current_dir = os.getcwd()
    print(f"📁 工作目录: {current_dir}")
    
    # 检查必要文件
    if not os.path.exists("gradlew.bat"):
        print("❌ 错误: gradlew.bat 不存在")
        return False
    
    if not os.path.exists("app/build.gradle"):
        print("❌ 错误: app/build.gradle 不存在")
        return False
    
    print("✅ 项目结构完整")
    
    # 1. 清理构建
    print("\n1. 🧹 清理之前的构建...")
    returncode, output = run_gradle_command("gradlew.bat clean")
    
    if returncode != 0:
        print(f"⚠️  清理警告 (代码: {returncode})")
    else:
        print("✅ 清理完成")
    
    # 2. 编译 Debug APK
    print("\n2. 🔨 编译 Debug APK...")
    print("   这可能需要 1-3 分钟，请耐心等待...")
    
    returncode, output = run_gradle_command("gradlew.bat assembleDebug")
    
    # 检查编译结果
    if "BUILD SUCCESSFUL" in output:
        print("✅ 编译成功！")
        success = True
    elif "BUILD FAILED" in output:
        print("❌ 编译失败")
        # 提取错误信息
        error_start = output.find("BUILD FAILED")
        if error_start != -1:
            error_msg = output[error_start:error_start+500]
            print(f"   错误: {error_msg}")
        success = False
    else:
        print(f"⚠️  编译状态未知 (返回码: {returncode})")
        success = returncode == 0
    
    if not success:
        return False
    
    # 3. 查找 APK 文件
    print("\n3. 🔍 查找生成的 APK 文件...")
    
    apk_search_paths = [
        "app/build/outputs/apk/debug/app-debug.apk",
        "app/build/outputs/apk/debug/*.apk",
        "app/build/outputs/apk/*/debug/*.apk",
        "app/build/outputs/*/debug/*.apk",
    ]
    
    apk_files = []
    for path_pattern in apk_search_paths:
        import glob
        matches = glob.glob(path_pattern)
        apk_files.extend(matches)
    
    # 去重
    apk_files = list(set(apk_files))
    
    if apk_files:
        print(f"✅ 找到 {len(apk_files)} 个 APK 文件:")
        for apk in apk_files:
            size_mb = os.path.getsize(apk) / 1024 / 1024
            print(f"   📱 {os.path.basename(apk)}")
            print(f"      路径: {apk}")
            print(f"      大小: {size_mb:.2f} MB")
        
        # 选择主要的 APK
        main_apk = None
        for apk in apk_files:
            if "app-debug.apk" in apk or "debug.apk" in apk:
                main_apk = apk
                break
        if not main_apk:
            main_apk = apk_files[0]
        
        # 复制到当前目录方便访问
        target_apk = "qrfileresconstructor-debug.apk"
        shutil.copy2(main_apk, target_apk)
        
        print(f"\n🎯 主 APK 已复制到: {target_apk}")
        print(f"   📏 大小: {os.path.getsize(target_apk) / 1024 / 1024:.2f} MB")
        
        print("\n📱 安装指南:")
        print("   1. 将 'qrfileresconstructor-debug.apk' 复制到手机")
        print("   2. 在手机文件管理器中找到该文件")
        print("   3. 点击安装（可能需要允许'安装未知来源应用'）")
        print("   4. 安装完成后打开应用测试")
        print("\n💡 测试建议:")
        print("   1. 先测试相机权限是否正常")
        print("   2. 使用之前模拟测试生成的二维码进行扫描")
        print("   3. 检查文件是否成功还原到 Download/QRReconstructor/ 目录")
        
        return True
    else:
        print("❌ 未找到任何 APK 文件")
        print("   尝试手动查找...")
        
        # 手动搜索
        apk_files_manual = []
        for root, dirs, files in os.walk("app/build"):
            for file in files:
                if file.endswith(".apk"):
                    full_path = os.path.join(root, file)
                    apk_files_manual.append(full_path)
        
        if apk_files_manual:
            print(f"   手动找到 {len(apk_files_manual)} 个 APK:")
            for apk in apk_files_manual[:3]:
                print(f"   - {apk}")
            return True
        else:
            print("   确实没有找到 APK 文件")
            return False
if __name__ == "__main__":
    success = main()
    utils.set_state(success=success, result="APK编译成功" if success else "APK编译失败")