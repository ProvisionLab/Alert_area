1. edit paths in build_mac.sh:

QTDIR - path where qt was installed. this path must contain macdeployqt tool

BUILD_DIR - the directory where BvcClient.app are building
use: find .. -name BvcClient.app

2. add execute permisions:
chmod +x build_mac.sh

3. create BvcClient.dmg:
./build_mac.sh
