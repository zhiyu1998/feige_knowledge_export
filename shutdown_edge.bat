@echo off
echo 正在关闭 Microsoft Edge 浏览器及其关联进程...

:: 关闭 Microsoft Edge 主进程
taskkill /F /IM msedge.exe

:: 关闭 Microsoft Edge 后台进程
taskkill /F /IM MicrosoftEdgeUpdate.exe

:: 关闭 Microsoft Edge 服务
sc stop edgeupdate
sc stop edgeupdatem

echo Microsoft Edge 及其关联进程已关闭。
pause