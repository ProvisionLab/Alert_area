#!/bin/sh

#path where qt was installed
QTDIR=~/Qt/5.9.2/clang_64/bin
#QTDIR=/usr/local/Cellar/qt/5.9.2/bin

APPNAME=ROG

if [ -d ../BvcClient/$APPNAME.app ]; then
  BUILD_DIR=../BvcClient
  BUNDLE_PATH=$BUILD_DIR/$APPNAME.app
else

  BUNDLE_PATH=`find ../build-*-Release -name $APPNAME.app -print -quit`
  BUILD_DIR=${BUNDLE_PATH%/*}
fi

if [ -z BUNDLE_PATH ]; then
  echo not fount bundle $APPNAME.app
  exit 1
fi

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

$QTDIR/macdeployqt $BUNDLE_PATH 

hdiutil create $APPNAME.dmg -srcfolder $BUNDLE_PATH -format UDZO -volname "$APPNAME volume"
