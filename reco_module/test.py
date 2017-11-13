from urllib.parse import urlsplit
from urllib.parse import quote


o = urlsplit('rtsp://1.2.3.4:500/')
#o.username = "username"
#o.password = "password"

print(quote("nabus@test.com"))
