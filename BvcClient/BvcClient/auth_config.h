#pragma once

#ifdef _DEBUG
#define BVCAPI_URL      "http://54.69.73.20:5000"   // BVC Dev
#else
#define BVCAPI_URL      "http://52.32.99.45:5000"   // BVC Prod
#endif
//#define BVCAPI_URL      "http://54.69.83.153:5000"  // server #2 EC2 instance (g3.4xlarge)
//#define BVCAPI_URL      "http://34.214.218.163:5000"  // server #3
//#define BVCAPI_URL      "http://192.168.88.247:5000"
//#define BVCAPI_URL      "http://localhost:5000"

#define BVCAPI_USERNAME "user1"
#define BVCAPI_PASSWORD "qwerty1"

#define ROGAPI_URL      "https://morning-lake-10802.herokuapp.com"

#ifdef _DEBUG
#define ROGAPI_USERNAME "nabus@test.com"
#define ROGAPI_PASSWORD "password123"
#endif
