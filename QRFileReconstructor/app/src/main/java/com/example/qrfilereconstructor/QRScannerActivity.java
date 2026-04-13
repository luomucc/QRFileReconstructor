package com.example.qrfilereconstructor;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.google.zxing.Result;
import me.dm7.barcodescanner.zxing.ZXingScannerView;
/**
 * 扫码界面
 * 使用 ZXingScannerView 进行快速集成
 */
public class QRScannerActivity extends AppCompatActivity implements ZXingScannerView.ResultHandler {
    private static final String TAG = "QRScannerActivity";
    private ZXingScannerView scannerView;
    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        scannerView = new ZXingScannerView(this);
        setContentView(scannerView);
    }
    @Override
    public void onResume() {
        super.onResume();
        scannerView.setResultHandler(this);
        scannerView.startCamera();
    }
    @Override
    public void onPause() {
        super.onPause();
        scannerView.stopCamera();
    }
    @Override
    public void handleResult(Result rawResult) {
        String contents = rawResult.getText();
        Log.d(TAG, "Scanned: " + contents);
        // 简单验证是否为 JSON 格式 (可选，防止误扫其他码)
        if (contents != null && contents.trim().startsWith("{")) {
            Intent resultIntent = new Intent();
            resultIntent.putExtra("SCAN_RESULT", contents);
            setResult(RESULT_OK, resultIntent);
            finish(); // 扫描成功，返回主界面
        } else {
            Toast.makeText(this, "非有效数据二维码，请重试", Toast.LENGTH_SHORT).show();
            // 延迟后继续扫描
            scannerView.resumeCameraPreview(this);
        }
    }
}