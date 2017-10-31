# Description

Server and client parts

## Getting started

Deploy on Ubuntu 16.04

### Prerequisites

* MongoDB
* Python3
* OpenCV3.x

### Build
#### OpenCV3.3

Download [Opencv3.3](https://github.com/opencv/opencv/archive/3.3.0.tar.gz)
And install in /usr/local via [tutorial](https://docs.opencv.org/3.0-beta/doc/tutorials/introduction/linux_install/linux_install.html)

#### MongoDB

Install mongoDB via [tutorial](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)

#### Client's part

build solution 
```
BvcClient/BvcClient/BvcClient.pro
```
run
```
./path_to__build/BvcClient
```

#### Server's part

install dependencies 

```
backend_server/dependencies.txt
```


### Configurations

#### MongoDB

run local instance of mongoDB

after that

```
python3 ./backend_server/create_test_db.py
```

#### Client's part

Users for test
```
User(1, 'reco1', 'reco1passwd')
User(2, 'user1', 'qwerty1')   
User(3, 'user2', 'qwerty2')
```

### Run

1. Run mongoDB instance (with created test database)
2. Run 
```
python3 backend_server/bvc_server.py
```
3. Run
```
./path_to_build/LvfClient
```

Now you can connect to testing database with test users.

