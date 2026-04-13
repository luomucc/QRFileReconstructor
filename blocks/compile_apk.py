import os
import subprocess
import sys
def main():
    print("=" * 50)
    print("  二维码文件重组工具 - APK 编译脚本")
    print("=" * 50)
    print()
    
    # 切换到项目目录
    project_dir = os.path.join(os.getcwd(), "QRFileReconstructor")
    if not os.path.exists(project_dir):
        print(f"❌ 错误：项目目录不存在: {project_dir}")
        print("请确保 QRFileReconstructor 文件夹存在。")
        return False
    
    os.chdir(project_dir)
    print(f"📁 切换到项目目录: {project_dir}")
    
    # 检查 gradlew.bat 是否存在
    gradlew_bat = os.path.join(project_dir, "gradlew.bat")
    if not os.path.exists(gradlew_bat):
        print(f"❌ 错误：gradlew.bat 不存在于 {project_dir}")
        return False
    
    try:
        # 1. 清理之前的构建
        print("\n1. 清理之前的构建...")
        result = subprocess.run([gradlew_bat, "clean"], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f"⚠️ 清理过程有警告: {result.stderr[:200]}")
        else:
            print("✅ 清理完成")
        
        # 2. 编译 Debug APK
        print("\n2. 开始编译 Debug APK...")
        print("   这可能需要几分钟，请耐心等待...")
        
        # 使用 subprocess.Popen 实时输出
        process = subprocess.Popen([gradlew_bat, "assembleDebug"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.STDOUT,
                                  text=True, encoding='utf-8')
        
        # 实时输出进度
        for line in process.stdout:
            # 过滤掉冗长的下载信息，只显示关键步骤
            if "Download" not in line and "> Task" in line:
                print(f"   {line.strip()}")
        
        process.wait()
        
        if process.returncode != 0:
            print("❌ APK 编译失败")
            return False
        
        # 3. 查找生成的 APK 文件
        print("\n3. 查找生成的 APK 文件...")
        apk_path = os.path.join(project_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
        
        if os.path.exists(apk_path):
            print(f"✅ APK 编译成功！")
            print(f"📱 APK 位置: {apk_path}")
            print(f"📏 文件大小: {os.path.getsize(apk_path) / 1024 / 1024:.2f} MB")
            print()
            print("🎯 安装指南:")
            print("   1. 将上面的 APK 文件复制到手机")
            print("   2. 在手机文件管理器中找到该文件")
            print("   3. 点击安装（可能需要允许'安装未知来源应用'）")
            print("   4. 安装完成后打开应用测试")
            return True
        else:
            print("❌ 错误：APK 文件未找到")
            # 尝试查找其他可能的路径
            for root, dirs, files in os.walk(os.path.join(project_dir, "app", "build")):
                for file in files:
                    if file.endswith(".apk"):
                        print(f"   找到可能的 APK: {os.path.join(root, file)}")
            return False
            
    except Exception as e:
        print(f"❌ 编译过程中出现异常: {e}")
        return False
if __name__ == "__main__":
    success = main()
    utils.set_state(success=success, result="APK编译完成" if success else "APK编译失败")