#!/bin/sh

QTDIR=~/Qt/5.8/clang_64
BUILD_DIR=../build-BvcClient-Desktop_Qt_5_8_0_clang_64bit-Release

APPNAME=BvcClient

$QTDIR/bin/macdeployqt $BUILD_DIR/$APPNAME.app -dmg

mv $BUILD_DIR/$APPNAME.dmg .
