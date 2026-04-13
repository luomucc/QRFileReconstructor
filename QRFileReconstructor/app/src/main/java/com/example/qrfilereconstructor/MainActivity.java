package com.example.qrfilereconstructor;
import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import java.io.File;
public class MainActivity extends AppCompatActivity implements FileReconstructor.ReconstructionListener {
    private static final int REQUEST_CAMERA_PERMISSION = 100;
    private static final int REQUEST_SCAN_CODE = 101;
    private TextView tvStatus;
    private TextView tvProgress;
    private Button btnScan;
    private Button btnReset;
    
    private FileReconstructor reconstructor;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        tvStatus = findViewById(R.id.tvStatus);
        tvProgress = findViewById(R.id.tvProgress);
        btnScan = findViewById(R.id.btnScan);
        btnReset = findViewById(R.id.btnReset);
        // 初始化重组器
        reconstructor = new FileReconstructor(this);
        btnScan.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                checkPermissionAndScan();
            }
        });
        btnReset.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                reconstructor.reset();
                updateUI(0, 0, "已重置，请开始扫描");
                Toast.makeText(MainActivity.this, "已重置", Toast.LENGTH_SHORT).show();
            }
        });
        
        updateUI(0, 0, "准备就绪");
    }
    private void checkPermissionAndScan() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.CAMERA},
                    REQUEST_CAMERA_PERMISSION);
        } else {
            startScanner();
        }
    }
    private void startScanner() {
        Intent intent = new Intent(this, QRScannerActivity.class);
        startActivityForResult(intent, REQUEST_SCAN_CODE);
    }
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CAMERA_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startScanner();
            } else {
                Toast.makeText(this, "需要相机权限才能扫码", Toast.LENGTH_LONG).show();
            }
        }
    }
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_SCAN_CODE && resultCode == RESULT_OK && data != null) {
            String scannedJson = data.getStringExtra("SCAN_RESULT");
            if (scannedJson != null) {
                tvStatus.setText("正在处理...");
                boolean isComplete = reconstructor.processChunk(scannedJson);
                if (!isComplete) {
                     // 如果未完成，可以选择自动继续扫码或者等待用户手动点击
                     // 这里为了用户体验，提示用户继续扫
                     Toast.makeText(this, "分片接收中...", Toast.LENGTH_SHORT).show();
                }
            }
        }
    }
    // --- 回调接口实现 ---
    @Override
    public void onProgress(int current, int total) {
        updateUI(current, total, "收集中...");
    }
    @Override
    public void onSuccess(File file, String message) {
        updateUI(reconstructor.getTotalCount(), reconstructor.getTotalCount(), message);
        Toast.makeText(this, "✅ " + message, Toast.LENGTH_LONG).show();
        // 可以在这里跳转到文件查看界面或者分享文件
    }
    @Override
    public void onError(String error) {
        tvStatus.setText("❌ 错误：" + error);
        Toast.makeText(this, "❌ " + error, Toast.LENGTH_LONG).show();
    }
    @Override
    public void onChecksumMismatch(String expected, String actual) {
        String msg = "校验失败！\n期望：" + expected + "\n实际：" + actual;
        tvStatus.setText("❌ " + msg);
        Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
        // 校验失败通常意味着数据损坏或扫描错误，建议重置
        reconstructor.reset();
        updateUI(0, 0, "校验失败，已重置");
    }
    private void updateUI(int current, int total, String statusText) {
        tvStatus.setText(statusText);
        if (total > 0) {
            tvProgress.setText(String.format("进度：%d / %d", current, total));
        } else {
            tvProgress.setText("进度：- / -");
        }
    }
}