# Description

The BVC software is composed of two parts, a client side and a server side. The client side allows a user to add/remove threat detection modules (Virtual Wall, Restricted Area, etc.) to their IP cameras by drawing them on the live camera feed. The server side receives the threat detection module parameters from the client and applies them. If a threat is detected, the server sends the alert data in POST requests to the ROG API.

On the client side, the user logs in with their ROG Monitor webapp credentials. The client sents a POST request to the ROG API's /api/v2/sessions endpoint and on successful login, sends a GET request to the ROG API's /api/v2/me/cameras endpoint to retrieve the RTSP URLs for the user's IP cameras.

On the server side, when a threat is first detected a POST request to the ROG API's /api/v2/bvc_alert endpoint is sent with the following data:

```
{
  alert_id: <string>,
  camera_id: <integer>,
  alert_type_id: <string>,
  timestamp: <ISO:Extended:Z>,
  image_1: <file>,
  image_2: <file>,
  image_3: <file>
}
```

where alert_id is the unique identifier for this alert, camera_id is the ROG API identifier for the camera, alert_type_id is the BVC identifier for the alert type, timestamp is the timestamp at which the threat was detected, image_1 is an image of the camera stream at timestamp - 2 seconds, image_2 at timestamp - seconds, and image_3 at timestamp.

Subsequent POST requests of more images for the same alert images include the following data:

```
{
  alert_id: <string>,
  image: <file>
}
``` 

## Installation

### Prerequisites

* Ubuntu 16.04
* MongoDB
* Python3
* OpenCV3.x
* tensorflow-gpu
* gunicorn

### Server installation

Clone the repository: https://github.com/ROG-Security/BVC then:

```
sudo apt-get install gunicorn3
cd /path/to/BVC/backend_server
chmod +x install.sh
./install.sh
cd /paht/to/BVC/reco_module
chmod +x install.sh
./install.sh
```

Update the configuration:

```
Open /path/to/BVC/backend_server/bvc_config.py and change the rogapi_url to the appropriate value for development or production.

Development rogapi_url should be https://rog-api-dev.herokuapp.com
```

```
Open /path/to/BVC/reco_module/reco_config.py and change the rogapi_url to the appropriate value for development or production.

Development rogapi_url should be https://rog-api-dev.herokuapp.com
```

Start the services:

```
cd /path/to/BVC/backend_server
./start.sh

cd /path/to/BVC/reco_module
./start.sh
```

### Client installation

### Build
#### OpenCV3.3

Download [Opencv3.3](https://github.com/opencv/opencv/archive/3.3.0.tar.gz)
And install in /usr/local via [tutorial](https://docs.opencv.org/3.0-beta/doc/tutorials/introduction/linux_install/linux_install.html)`

#### Download and install Qt (5.8+)

### Install OpenVC (3.2+)

```
sudo apt-get install pkgconfig libopencv-dev
```

### Build solution 

Open /path/to/BVC/BvcClient/BvcClient/BvcClient.pro in QT and build. Once built, run the executable:

```
cd /path/to/build/
./BvcClient
```