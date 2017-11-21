rem change paths

set QTDIR=d:\dev\qt
set QTKIT=5.9.2\msvc2017_64
set BUILD_DIR=..\build-BvcClient-Desktop_Qt_5_9_2_MSVC2017_64bit_Fixed-Release
rem set OPENCV_DIR=d:\dev\OpenCV320\opencv\build
set OPENCV_BIN=%OPENCV_DIR%\x64\vc14\bin

set PACKAGEDIR=.\packages\com.rog.tool\data
set APPNAME=RogTool.exe

rem prepare files

del /Q /S "%PACKAGEDIR%\*"

rem call "%VS150COMNTOOLS%vsvars32.bat"
set VCINSTALLDIR=%VS150COMNTOOLS%..\..\VC\
rem set > aaa

"%QTDIR%\%QTKIT%\bin\windeployqt" -dir "%PACKAGEDIR%" ^
    --compiler-runtime --no-system-d3d-compiler --no-translations --no-opengl-sw --release ^
    "%BUILD_DIR%\ROG.exe"

copy "%BUILD_DIR%\ROG.exe" "%PACKAGEDIR%\%APPNAME%"
copy "%OPENCV_BIN%\opencv_ffmpeg320_64.dll" "%PACKAGEDIR%\opencv_ffmpeg320_64.dll"
copy "%OPENCV_BIN%\opencv_world320.dll" "%PACKAGEDIR%\opencv_world320.dll"
copy "..\BvcClient\rog_256.ico" "%PACKAGEDIR%\rog.ico"

rem sign

DigiCertUtil.exe sign /sha1 "07639818f447f2fa350e04ab3bf4b602e9930116" "%PACKAGEDIR%\%APPNAME%"

rem build installer

"%QTDIR%\Tools\QtInstallerFramework\3.0\bin\binarycreator.exe" --offline-only -c config\config.xml -p packages RogToolInstaller64.exe

DigiCertUtil.exe sign /sha1 "07639818f447f2fa350e04ab3bf4b602e9930116" RogToolInstaller64.exe

