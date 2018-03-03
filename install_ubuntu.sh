#!/bin/sh

chmod +x backend_server/install.sh
chmod +x backend_server/start.sh
cd backend_server
./install.sh
cd ..

chmod +x reco_module/install.sh
chmod +x reco_module/start.sh
cd reco_module
./install.sh
cd ..

chmod +x start.sh
