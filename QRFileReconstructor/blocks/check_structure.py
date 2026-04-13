import os
def check_project_structure():
    print("📁 检查当前目录结构...")
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    print("\n📋 目录内容:")
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if os.path.isdir(item_path):
            size = "目录"
        else:
            size = f"{os.path.getsize(item_path):,} 字节"
        print(f"  - {item} ({size})")
    
    # 检查 QRFileReconstructor 是否存在
    qr_dir = os.path.join(current_dir, "QRFileReconstructor")
    if os.path.exists(qr_dir):
        print(f"\n✅ QRFileReconstructor 目录存在")
        
        # 检查关键文件
        key_files = [
            ("gradlew.bat", os.path.join(qr_dir, "gradlew.bat")),
            ("app/build.gradle", os.path.join(qr_dir, "app", "build.gradle")),
            ("src/main/java", os.path.join(qr_dir, "app", "src", "main", "java")),
        ]
        
        for name, path in key_files:
            if os.path.exists(path):
                print(f"  ✅ {name} 存在")
            else:
                print(f"  ❌ {name} 不存在")
        
        return qr_dir
    else:
        print(f"\n❌ QRFileReconstructor 目录不存在")
        return None
if __name__ == "__main__":
    project_dir = check_project_structure()
    utils.set_state(success=project_dir is not None, result=project_dir)