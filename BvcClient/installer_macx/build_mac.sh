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

echo ==== patch =================

for f in $BUNDLE_PATH/Contents/Frameworks/lib*.dylib; do
    F2L=`otool -L $f  | grep /usr/local/ | cut -f 2 | cut -f 1 -d ' '`
    if [ ! -z "$F2L" ]; then
        echo patch: $f
        fb=`basename $f`
        for f2 in $F2L; do
            f2b=`basename $f2`
            echo $fb $f2 $f2b
            if [ "$fb" = "$f2b" ]; then
                echo change id of $f
                install_name_tool -id @executable_path/../Frameworks/$fb $f
            else
                install_name_tool -change $f2 @executable_path/../Frameworks/$f2b $f
            fi
        done
    fi
done

echo ==== check begin =================

for f in $BUNDLE_PATH/Contents/Frameworks/lib*.dylib; do
    for f2 in `otool -L $f  | grep /usr/local/ | cut -f 2 | cut -f 1 -d ' '`; do
        echo $f `basename $f2`
    done
done

echo ==== check end =================

$QTDIR/macdeployqt $BUNDLE_PATH -dmg

mv $BUILD_DIR/$APPNAME.dmg .
