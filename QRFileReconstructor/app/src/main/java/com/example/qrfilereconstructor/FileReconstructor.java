package com.example.qrfilereconstructor;
import android.util.Base64;
import android.util.Log;
import org.json.JSONObject;
import java.io.File;
import java.io.FileOutputStream;
import java.security.MessageDigest;
import java.util.TreeMap;
/**
 * 核心重组逻辑类
 * 负责管理分片数据，判断是否收集完毕，执行拼接、解码和校验
 */
public class FileReconstructor {
    private static final String TAG = "FileReconstructor";
    
    // 使用 TreeMap 自动按 currentPackageNumber 排序
    private TreeMap<Integer, String> dataChunks;
    private int totalPackages = 0;
    private String fileName = "reconstructed_file";
    private String expectedChecksum = "";
    private String encoding = "Base64";
    
    // 回调接口，用于通知 UI 进度和结果
    public interface ReconstructionListener {
        void onProgress(int current, int total);
        void onSuccess(File file, String message);
        void onError(String error);
        void onChecksumMismatch(String expected, String actual);
    }
    
    private ReconstructionListener listener;
    public FileReconstructor(ReconstructionListener listener) {
        this.listener = listener;
        reset();
    }
    /**
     * 重置状态，准备新一轮接收
     */
    public void reset() {
        dataChunks = new TreeMap<>();
        totalPackages = 0;
        fileName = "reconstructed_file";
        expectedChecksum = "";
        encoding = "Base64";
        Log.d(TAG, "Reconstructor reset.");
    }
    /**
     * 处理扫描到的 JSON 数据
     * @param jsonStr 扫描二维码获得的 JSON 字符串
     * @return true 如果这是最后一个包且开始重组，false 表示还在收集中
     */
    public boolean processChunk(String jsonStr) {
        try {
            JSONObject json = new JSONObject(jsonStr);
            
            int currentNum = json.getInt("currentPackageNumber");
            int total = json.getInt("totalPackages");
            String content = json.getString("dataContent");
            
            // 初始化总数和文件名 (假设所有包的这些信息一致，以第一个包为准)
            if (totalPackages == 0) {
                totalPackages = total;
                fileName = json.optString("fileName", "reconstructed_file");
                expectedChecksum = json.optString("checksum", "");
                encoding = json.optString("encoding", "Base64");
                Log.d(TAG, "Initiated: Total=" + totalPackages + ", File=" + fileName);
            }
            
            // 检查总数是否一致
            if (total != totalPackages) {
                if (listener != null) listener.onError("包总数不一致！期望:" + totalPackages + " 实际:" + total);
                return false;
            }
            // 存入 TreeMap (自动排序)
            dataChunks.put(currentNum, content);
            
            if (listener != null) {
                listener.onProgress(dataChunks.size(), totalPackages);
            }
            
            Log.d(TAG, "Received chunk " + currentNum + "/" + totalPackages);
            // 检查是否收集完毕
            if (dataChunks.size() == totalPackages) {
                reconstructFile();
                return true; // 完成
            }
            
            return false; // 未完成
            
        } catch (Exception e) {
            Log.e(TAG, "Error processing chunk", e);
            if (listener != null) listener.onError("解析 JSON 失败：" + e.getMessage());
            return false;
        }
    }
    /**
     * 执行文件重组
     */
    private void reconstructFile() {
        try {
            StringBuilder fullDataBuilder = new StringBuilder();
            for (String chunk : dataChunks.values()) {
                fullDataBuilder.append(chunk);
            }
            
            String fullDataBase64 = fullDataBuilder.toString();
            byte[] fileBytes;
            
            if ("Base64".equalsIgnoreCase(encoding)) {
                fileBytes = Base64.decode(fullDataBase64, Base64.DEFAULT);
            } else {
                // 如果不是 Base64，直接取字节 (假设是纯文本或其他编码，这里简化处理)
                fileBytes = fullDataBase64.getBytes();
            }
            
            // 计算实际 Checksum (MD5)
            String actualChecksum = calculateMD5(fileBytes);
            
            // 校验
            if (expectedChecksum != null && !expectedChecksum.isEmpty() && !expectedChecksum.equalsIgnoreCase(actualChecksum)) {
                if (listener != null) listener.onChecksumMismatch(expectedChecksum, actualChecksum);
                return;
            }
            
            // 保存文件 (保存到应用私有目录或外部存储，此处演示保存到外部存储 Download 目录)
            // 注意：Android 10+ 需要使用 MediaStore 或 getExternalFilesDir
            File outputDir = new File(android.os.Environment.getExternalStoragePublicDirectory(android.os.Environment.DIRECTORY_DOWNLOADS), "QRReconstructor");
            if (!outputDir.exists()) {
                outputDir.mkdirs();
            }
            
            File outputFile = new File(outputDir, fileName);
            FileOutputStream fos = new FileOutputStream(outputFile);
            fos.write(fileBytes);
            fos.close();
            
            Log.d(TAG, "File saved to: " + outputFile.getAbsolutePath());
            if (listener != null) listener.onSuccess(outputFile, "文件还原成功！大小：" + fileBytes.length + " 字节");
            
            // 完成后自动重置，准备下一次任务 (可选)
            // reset(); 
            
        } catch (Exception e) {
            Log.e(TAG, "Error reconstructing file", e);
            if (listener != null) listener.onError("文件重组失败：" + e.getMessage());
        }
    }
    
    /**
     * 计算字节数组的 MD5 值
     */
    private String calculateMD5(byte[] data) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] digest = md.digest(data);
        StringBuilder sb = new StringBuilder();
        for (byte b : digest) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
    
    /**
     * 获取当前进度
     */
    public int getCurrentCount() {
        return dataChunks.size();
    }
    
    public int getTotalCount() {
        return totalPackages;
    }
}