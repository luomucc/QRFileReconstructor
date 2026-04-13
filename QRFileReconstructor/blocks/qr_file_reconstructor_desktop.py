"""
桌面版二维码文件重组工具
功能：模拟安卓 App 的核心功能，可以在电脑上测试二维码分片重组
"""
import json
import base64
import hashlib
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import io
class QRFileReconstructorDesktop:
    """桌面版文件重组器"""
    def __init__(self):
        self.data_chunks = {}  # 存储分片数据
        self.total_packages = 0
        self.file_name = ""
        self.expected_checksum = ""
        self.encoding = "Base64"
        
    def process_chunk(self, json_str):
        """处理一个二维码分片"""
        try:
            data = json.loads(json_str)
            
            current_num = data["currentPackageNumber"]
            total = data["totalPackages"]
            content = data["dataContent"]
            
            # 初始化信息
            if self.total_packages == 0:
                self.total_packages = total
                self.file_name = data.get("fileName", "reconstructed_file")
                self.expected_checksum = data.get("checksum", "")
                self.encoding = data.get("encoding", "Base64")
                print(f"初始化: 总分片={total}, 文件名={self.file_name}")
            
            # 检查总数一致性
            if total != self.total_packages:
                return False, f"包总数不一致！期望:{self.total_packages} 实际:{total}"
            
            # 存储分片
            self.data_chunks[current_num] = content
            print(f"收到分片 {current_num}/{self.total_packages}")
            
            # 检查是否完成
            if len(self.data_chunks) == self.total_packages:
                return True, "所有分片收集完毕"
            else:
                return False, f"进度: {len(self.data_chunks)}/{self.total_packages}"
                
        except Exception as e:
            return False, f"解析错误: {str(e)}"
    
    def reconstruct_file(self):
        """重组文件"""
        if len(self.data_chunks) != self.total_packages:
            return False, f"分片不完整: {len(self.data_chunks)}/{self.total_packages}"
        
        try:
            # 按序号排序拼接
            sorted_keys = sorted(self.data_chunks.keys())
            full_data = "".join([self.data_chunks[k] for k in sorted_keys])
            
            # 解码
            if self.encoding.lower() == "base64":
                file_bytes = base64.b64decode(full_data)
            else:
                file_bytes = full_data.encode()
            
            # 计算校验码
            actual_checksum = hashlib.md5(file_bytes).hexdigest()
            
            # 校验
            if self.expected_checksum and self.expected_checksum != actual_checksum:
                return False, f"校验失败！期望:{self.expected_checksum} 实际:{actual_checksum}"
            
            # 保存文件
            save_path = filedialog.asksaveasfilename(
                defaultextension=".*",
                initialfile=self.file_name,
                title="保存重组后的文件"
            )
            
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(file_bytes)
                
                return True, f"文件保存成功！\n路径: {save_path}\n大小: {len(file_bytes):,} 字节\nMD5: {actual_checksum}"
            else:
                return False, "用户取消保存"
                
        except Exception as e:
            return False, f"重组错误: {str(e)}"
    
    def reset(self):
        """重置状态"""
        self.data_chunks = {}
        self.total_packages = 0
        self.file_name = ""
        self.expected_checksum = ""
        self.encoding = "Base64"
        print("状态已重置")
class QRGenerator:
    """二维码生成器（用于测试）"""
    @staticmethod
    def create_test_file():
        """创建测试文件并生成分片二维码"""
        # 选择文件
        file_path = filedialog.askopenfilename(title="选择要分片的文件")
        if not file_path:
            return None
        
        # 读取文件
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        file_name = os.path.basename(file_path)
        file_md5 = hashlib.md5(file_data).hexdigest()
        base64_data = base64.b64encode(file_data).decode('utf-8')
        
        # 询问分片数量
        root = tk.Tk()
        root.withdraw()
        
        from tkinter import simpledialog
        total_packages = simpledialog.askinteger(
            "分片数量",
            f"文件大小: {len(file_data):,} 字节\n请输入分片数量:",
            minvalue=1,
            maxvalue=20,
            initialvalue=3
        )
        
        if not total_packages:
            return None
        
        # 分片
        chunk_size = len(base64_data) // total_packages + 1
        chunks = []
        
        for i in range(total_packages):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(base64_data))
            chunk_data = base64_data[start:end]
            
            if not chunk_data:
                continue
            
            chunk_json = {
                "totalPackages": total_packages,
                "currentPackageNumber": i + 1,
                "encoding": "Base64",
                "dataLength": len(chunk_data),
                "dataContent": chunk_data,
                "fileName": file_name,
                "checksum": file_md5
            }
            
            chunks.append(chunk_json)
        
        return chunks
class DesktopApp:
    """桌面应用程序"""
    def __init__(self, root):
        self.root = root
        self.root.title("二维码文件重组工具 - 桌面版")
        self.root.geometry("600x700")
        
        self.reconstructor = QRFileReconstructorDesktop()
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_label = ttk.Label(
            self.root,
            text="📦 二维码文件重组工具",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        # 状态显示
        self.status_frame = ttk.LabelFrame(self.root, text="状态", padding=10)
        self.status_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_label = ttk.Label(
            self.status_frame,
            text="进度: 0/0",
            font=("Arial", 14)
        )
        self.progress_label.pack()
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="准备就绪",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        # 控制按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="📷 输入二维码数据",
            command=self.input_qr_data,
            width=20
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 重置",
            command=self.reset,
            width=15
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 重组并保存文件",
            command=self.reconstruct,
            width=20
        ).pack(side="left", padx=5)
        
        # 测试工具
        test_frame = ttk.LabelFrame(self.root, text="测试工具", padding=10)
        test_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(
            test_frame,
            text="🔧 生成测试二维码",
            command=self.generate_test_qr,
            width=20
        ).pack()
        
        ttk.Label(
            test_frame,
            text="（用于生成测试数据，模拟分片二维码）",
            font=("Arial", 9)
        ).pack(pady=5)
        
        # 日志显示
        log_frame = ttk.LabelFrame(self.root, text="操作日志", padding=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, width=60)
        self.log_text.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def log(self, message):
        """添加日志"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        print(message)
    
    def input_qr_data(self):
        """输入二维码数据"""
        dialog = tk.Toplevel(self.root)
        dialog.title("输入二维码数据")
        dialog.geometry("500x300")
        
        ttk.Label(dialog, text="请输入扫描到的 JSON 数据:", font=("Arial", 12)).pack(pady=10)
        
        text_area = tk.Text(dialog, height=10, width=60)
        text_area.pack(padx=10, pady=5)
        
        def submit():
            json_str = text_area.get("1.0", "end").strip()
            if not json_str:
                messagebox.showerror("错误", "请输入 JSON 数据")
                return
            
            try:
                # 验证 JSON 格式
                json.loads(json_str)
                
                # 处理分片
                is_complete, message = self.reconstructor.process_chunk(json_str)
                
                # 更新界面
                current = len(self.reconstructor.data_chunks)
                total = self.reconstructor.total_packages
                
                self.progress_label.config(text=f"进度: {current}/{total}")
                self.status_label.config(text=message)
                
                self.log(f"✅ 处理分片: {message}")
                
                if is_complete:
                    messagebox.showinfo("完成", "所有分片收集完毕！点击'重组并保存文件'按钮保存文件。")
                
                dialog.destroy()
                
            except json.JSONDecodeError:
                messagebox.showerror("错误", "无效的 JSON 格式")
            except Exception as e:
                messagebox.showerror("错误", f"处理失败: {str(e)}")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="提交", command=submit).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side="left", padx=5)
    
    def reset(self):
        """重置"""
        self.reconstructor.reset()
        self.progress_label.config(text="进度: 0/0")
        self.status_label.config(text="已重置")
        self.log("🔄 状态已重置")
    
    def reconstruct(self):
        """重组文件"""
        if len(self.reconstructor.data_chunks) == 0:
            messagebox.showwarning("警告", "还没有输入任何分片数据")
            return
        
        success, message = self.reconstructor.reconstruct_file()
        
        if success:
            messagebox.showinfo("成功", message)
            self.log(f"💾 {message}")
            # 成功后自动重置
            self.reset()
        else:
            messagebox.showerror("失败", message)
            self.log(f"❌ {message}")
    
    def generate_test_qr(self):
        """生成测试二维码"""
        chunks = QRGenerator.create_test_file()
        
        if not chunks:
            return
        
        # 显示二维码
        qr_window = tk.Toplevel(self.root)
        qr_window.title("测试二维码")
        qr_window.geometry("500x600")
        
        ttk.Label(
            qr_window,
            text=f"共 {len(chunks)} 个分片二维码",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        # 创建笔记本标签页
        notebook = ttk.Notebook(qr_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i, chunk in enumerate(chunks):
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=f"分片 {i+1}")
            
            # 显示 JSON 数据
            json_text = tk.Text(frame, height=8, width=50)
            json_text.pack(padx=10, pady=5)
            json_text.insert("1.0", json.dumps(chunk, indent=2))
            json_text.config(state="disabled")
            
            # 生成二维码图片
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(chunk))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为 PhotoImage
            img_tk = ImageTk.PhotoImage(img)
            
            label = ttk.Label(frame, image=img_tk)
            label.image = img_tk  # 保持引用
            label.pack(pady=5)
        
        ttk.Button(
            qr_window,
            text="关闭",
            command=qr_window.destroy
        ).pack(pady=10)
        
        self.log(f"🔧 生成了 {len(chunks)} 个测试二维码")
def main():
    """主函数"""
    root = tk.Tk()
    app = DesktopApp(root)
    
    # 显示使用说明
    messagebox.showinfo(
        "使用说明",
        "📱 二维码文件重组工具 - 桌面版\n\n"
        "使用方法:\n"
        "1. 点击'生成测试二维码'创建测试数据\n"
        "2. 用手机扫描生成的二维码\n"
        "3. 点击'输入二维码数据'粘贴扫描结果\n"
        "4. 重复直到所有分片收集完毕\n"
        "5. 点击'重组并保存文件'保存还原的文件\n\n"
        "或者直接输入您的二维码分片数据进行测试。"
    )
    
    root.mainloop()
if __name__ == "__main__":
    main()
    utils.set_state(success=True, result="桌面版应用启动成功")