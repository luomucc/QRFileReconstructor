import os
import subprocess
def get_detailed_gradle_error():
    """获取详细的 Gradle 错误信息"""
    print("🔍 检查 Gradle 详细错误...")
    
    # 直接运行 gradlew.bat 查看版本信息，这通常能暴露环境问题
    print("\n1. 检查 Gradle 版本...")
    result = subprocess.run(
        ["gradlew.bat", "--version"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    print(f"返回码: {result.returncode}")
    if result.stdout:
        print("输出:")
        print(result.stdout[:500])
    if result.stderr:
        print("错误:")
        print(result.stderr[:500])
    
    # 尝试运行一个简单的任务
    print("\n2. 尝试运行简单任务...")
    result = subprocess.run(
        ["gradlew.bat", "tasks", "--all"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        timeout=30
    )
    
    print(f"返回码: {result.returncode}")
    if result.returncode != 0 and result.stderr:
        print("错误详情:")
        print(result.stderr)
    
    # 检查 Android SDK 环境变量
    print("\n3. 检查环境变量...")
    env_vars = ["ANDROID_HOME", "ANDROID_SDK_ROOT", "JAVA_HOME"]
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: 未设置")
    
    # 检查本地 Gradle 缓存
    gradle_user_home = os.environ.get("GRADLE_USER_HOME", os.path.expanduser("~/.gradle"))
    print(f"\n4. Gradle 用户目录: {gradle_user_home}")
    if os.path.exists(gradle_user_home):
        print(f"  ✅ 目录存在")
    else:
        print(f"  ⚠️ 目录不存在")
    
    return result.returncode
def check_build_files():
    """检查构建文件"""
    print("\n📄 检查构建文件...")
    
    files_to_check = [
        ("build.gradle", "根构建文件"),
        ("app/build.gradle", "模块构建文件"),
        ("settings.gradle", "项目设置文件"),
        ("gradle/wrapper/gradle-wrapper.properties", "Gradle包装器配置"),
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"  ✅ {filename} ({description}) 存在")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    print(f"      行数: {lines}")
                    # 显示关键内容
                    if filename == "app/build.gradle":
                        if "compileSdk" in content:
                            print(f"      包含 compileSdk 配置")
                        if "dependencies" in content:
                            print(f"      包含 dependencies 配置")
            except:
                print(f"      无法读取内容")
        else:
            print(f"  ❌ {filename} ({description}) 不存在")
if __name__ == "__main__":
    print("=" * 60)
    print("       Gradle 环境诊断")
    print("=" * 60)
    
    check_build_files()
    returncode = get_detailed_gradle_error()
    
    print("\n📋 诊断总结:")
    if returncode == 0:
        print("✅ Gradle 环境正常，可能是其他编译错误")
    else:
        print("❌ Gradle 环境有问题")
        print("\n💡 可能的原因:")
        print("   1. 缺少 Android SDK")
        print("   2. Java 版本不兼容")
        print("   3. Gradle 包装器损坏")
        print("   4. 网络问题导致依赖下载失败")
    
    utils.set_state(success=returncode==0, result=f"Gradle诊断完成，返回码: {returncode}")