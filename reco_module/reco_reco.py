from reco_client import post_reco_alert, get_camera_alerts
import threading
import time
import cv2

# camera: { 'id' : str, 'url' : str }

# alert: 
#{ 
#   'id' : str, 
#   'type' : 'RA'|'LD'|'VW', 
#   'points': [[x1,y1],[x2,y2],[x3,y3]],     # [x,y] are relative to frame size
#   'duration' : int,                        # seconds, for type="LD"
#   'direction' : 'B'|'L'|'R',               # for type="VW", both/to_left/to_right
#}

thread_count = 0
bStop = False

def stop_recognition():

  global bStop
  bStop = True
  pass

def wait_threads():

  while thread_count > 0:
    time.sleep(1)

  pass

class RecoThread(threading.Thread):

  access_token = None
  camera = None
  alerts = None

  n = 0

  def process_frame(self, frame):

    if (self.n % 60) == 0:
      camera_id = self.camera['id']
      alert_id = self.alerts[0]['id']
      post_reco_alert(self.access_token, camera_id, alert_id)  
 
    self.n += 1
    pass

  def run(self):

    print('start reco: {0}'.format(self.camera['url']))

    # open stream by url
    camera_url = self.camera['url']
    camera_id = self.camera['id']

    self.alerts = get_camera_alerts(self.access_token, camera_id)

#    try:
    if True:
      cap = cv2.VideoCapture(camera_url)
    
      if cap.isOpened():

        while not bStop and cap.isOpened():

          res, frame = cap.read()

          if not res:
            break;

          self.process_frame(frame)
          #cv2.imshow('video', frame)
          #cv2.imwrite('1.jpg', frame)

          # update alerts
          if (self.n % 60*20) == 0:
            self.alerts = get_camera_alerts(self.access_token, camera_id)
     
      cap.release()
      print('end: {0}'.format(camera_id))

#    except:
#      print('exception: {0}'.format(camera_id))
#      pass
  
    global thread_count
    thread_count -= 1

    pass      


def start_recognition(access_token:str, camera:dict):

  global thread_count
  thread_count += 1

  t = RecoThread()
  t.access_token = access_token
  t.camera = camera
  t.start()
  
  pass
