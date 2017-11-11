#!/bin/sh

#path where qt was installed
QTDIR=~/Qt/5.8/clang_64/bin
#QTDIR=/usr/local/Cellar/qt/5.9.2/bin

#path where BvcClient.app are building
BUILD_DIR=../build-BvcClient-Desktop_Qt_5_8_0_clang_64bit-Release
#BUILD_DIR=../BvcClient

APPNAME=BvcClient

$QTDIR/macdeployqt $BUILD_DIR/$APPNAME.app -dmg

mv $BUILD_DIR/$APPNAME.dmg .
