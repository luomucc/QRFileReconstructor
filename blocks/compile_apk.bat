@echo off
echo ========================================
echo  二维码文件重组工具 - APK 编译脚本
echo ========================================
echo.
REM 切换到项目目录
cd /d "%~dp0QRFileReconstructor"
echo 1. 清理之前的构建...
call gradlew.bat clean
echo.
echo 2. 开始编译 Debug APK...
call gradlew.bat assembleDebug
echo.
echo 3. 查找生成的 APK 文件...
if exist app\build\outputs\apk\debug\app-debug.apk (
    echo ✅ APK 编译成功！
    echo APK 位置: %cd%\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo 请将此 APK 文件复制到手机安装测试。
) else (
    echo ❌ APK 编译失败，请检查错误信息。
    pause
)