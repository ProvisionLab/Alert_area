# Description

Server and client parts

## Getting started

Deploy on Ubuntu 16.04

### Prerequisites

* MongoDB
* Python3
* OpenCV3.x

### Build

#### Client's part

build solution 
```
BvcClient/BvcClient/BvcClient.pro
```
run
```
./path_to__build/LvfClient
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

