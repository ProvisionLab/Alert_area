#!/bin/sh

#path where qt was installed
QTDIR=~/Qt/5.8/clang_64/bin
#QTDIR=/usr/local/Cellar/qt/5.9.2/bin

#path where BvcClient.app are building
BUILD_DIR=../build-BvcClient-Desktop_Qt_5_8_0_clang_64bit-Release
#BUILD_DIR=../BvcClient

APPNAME=BvcClient
BUNDLE_PATH=$BUILD_DIR/$APPNAME.app

$QTDIR/macdeployqt $BUNDLE_PATH

install_name_tool -change /usr/local/Cellar/ilmbase/2.2.0/lib/libIex-2_2.12.dylib @executable_path/../Frameworks/libIex-2_2.12.dylib "$BUNDLE_PATH/Contents/Frameworks/libImath-2_2.12.dylib"
install_name_tool -change /usr/local/Cellar/ilmbase/2.2.0/lib/libIex-2_2.12.dylib @executable_path/../Frameworks/libIex-2_2.12.dylib "$BUNDLE_PATH/Contents/Frameworks/libIexMath-2_2.12.dylib"
install_name_tool -change /usr/local/Cellar/ilmbase/2.2.0/lib/libIex-2_2.12.dylib @executable_path/../Frameworks/libIex-2_2.12.dylib "$BUNDLE_PATH/Contents/Frameworks/libIlmThread-2_2.12.dylib"

$QTDIR/macdeployqt $BUNDLE_PATH -dmg

mv $BUILD_DIR/BvcClient.dmg .
