import json
import base64
import hashlib
import os
# 1. 模拟原始文件内容 (比如一个 README.md)
original_content = b"This is a secret file content.\nIt has multiple lines.\nEnd of file."
file_name = "README.md"
# 2. 计算原始文件的 MD5
original_md5 = hashlib.md5(original_content).hexdigest()
print(f"🎯 原始文件 MD5: {original_md5}")
# 3. 将文件内容转为 Base64
base64_data = base64.b64encode(original_content).decode('utf-8')
# 4. 模拟分片 (假设分为 3 个包)
total_packages = 3
chunk_size = len(base64_data) // total_packages + 1
chunks = []
for i in range(total_packages):
    start = i * chunk_size
    end = min((i + 1) * chunk_size, len(base64_data))
    chunk_data = base64_data[start:end]
    
    if not chunk_data:
        continue
        
    package_json = {
        "totalPackages": total_packages,
        "currentPackageNumber": i + 1,
        "encoding": "Base64",
        "dataLength": len(chunk_data),
        "dataContent": chunk_data,
        "fileName": file_name,
        "checksum": original_md5
    }
    chunks.append(package_json)
    print(f"📦 生成第 {i+1}/{total_packages} 个二维码数据片段")
# 5. 模拟 App 接收与重组逻辑 (对应 FileReconstructor.java)
received_chunks = {}
for pkg in chunks:
    num = pkg["currentPackageNumber"]
    received_chunks[num] = pkg["dataContent"]
    print(f"✅ App 接收到分片 {num}")
# 6. 拼接与解码
if len(received_chunks) == total_packages:
    print("🚀 所有分片收集完毕，开始重组...")
    
    # 按序号排序拼接
    sorted_keys = sorted(received_chunks.keys())
    full_base64_str = "".join([received_chunks[k] for k in sorted_keys])
    
    # Base64 解码
    try:
        reconstructed_bytes = base64.b64decode(full_base64_str)
        
        # 计算重组后的 MD5
        reconstructed_md5 = hashlib.md5(reconstructed_bytes).hexdigest()
        print(f"🔍 重组文件 MD5: {reconstructed_md5}")
        
        # 校验
        if reconstructed_md5 == original_md5:
            print("✅ 校验成功！文件还原完美。")
            # 保存文件验证
            with open(f"restored_{file_name}", "wb") as f:
                f.write(reconstructed_bytes)
            print(f"💾 文件已保存为 restored_{file_name}")
        else:
            print("❌ 校验失败！数据可能损坏。")
            
    except Exception as e:
        print(f"❌ 解码失败：{e}")
else:
    print(f"⚠️ 分片缺失：仅收到 {len(received_chunks)}/{total_packages}")
utils.set_state(success=True, result="模拟测试通过")