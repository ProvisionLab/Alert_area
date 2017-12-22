#pragma once

#define USE_ROG_DEV_SERVER  1


#if USE_ROG_DEV_SERVER

    #define BVCAPI_URL      "http://54.69.73.20:5000"   // BVC Dev
    //#define BVCAPI_URL      "http://54.69.83.153:5000"  // server #2 EC2 instance (g3.4xlarge)
    //#define BVCAPI_URL      "http://34.214.218.163:5000"  // server #3
    //#define BVCAPI_URL      "http://192.168.88.247:5000"
    //#define BVCAPI_URL      "http://localhost:5000"

    #define ROGAPI_URL      "https://rog-api-dev.herokuapp.com"

    #ifdef _DEBUG
        #define ROGAPI_USERNAME "bvc-dev@gorog.co"
        #define ROGAPI_PASSWORD "password123!!!"
    #endif

#else

    #define BVCAPI_URL      "http://52.32.99.45:5000"   // BVC Prod

    #define ROGAPI_URL      "https://morning-lake-10802.herokuapp.com"

    #ifdef _DEBUG
        #define ROGAPI_USERNAME "nabus@test.com"
        #define ROGAPI_PASSWORD "password123"
    #endif

#endif

#define BVCAPI_USERNAME "rogt-1"
#define BVCAPI_PASSWORD "qwerty1"
