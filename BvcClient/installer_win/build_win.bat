rem change paths

set QTDIR=d:\dev\qt
set QTKIT=5.9.2\msvc2017_64
set BUILD_DIR=..\build-BvcClient-Desktop_Qt_5_9_2_MSVC2017_64bit_Fixed-Release
rem set OPENCV_DIR=d:\dev\OpenCV320\opencv\build
set OPENCV_BIN=%OPENCV_DIR%\x64\vc14\bin

set PACKAGEDIR=.\packages\com.bvc.client\data
set APPNAME=BvcClient.exe

rem prepare files

del /Q /S "%PACKAGEDIR%\*"

call "%VS140COMNTOOLS%vsvars32.bat"

"%QTDIR%\%QTKIT%\bin\windeployqt" -dir "%PACKAGEDIR%" ^
    --compiler-runtime --no-system-d3d-compiler --no-translations --no-opengl-sw --release ^
    "%BUILD_DIR%\%APPNAME%"

copy "%BUILD_DIR%\%APPNAME%" "%PACKAGEDIR%\%APPNAME%"
copy "%OPENCV_BIN%\opencv_ffmpeg320_64.dll" "%PACKAGEDIR%\opencv_ffmpeg320_64.dll"
copy "%OPENCV_BIN%\opencv_world320.dll" "%PACKAGEDIR%\opencv_world320.dll"
copy "..\BvcClient\bvc.png" "%PACKAGEDIR%\bvc.png"
copy "..\BvcClient\bvc.ico" "%PACKAGEDIR%\bvc.ico"

rem build installer

"%QTDIR%\Tools\QtInstallerFramework\3.0\bin\binarycreator.exe" --offline-only -c config\config.xml -p packages BvcClientInstaller64.exe
