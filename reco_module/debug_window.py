import cv2
from reco_client import get_camera_alerts
import numpy as np

class DebugWindow:

    bbox_color = (0, 255, 0)

    alerts = None

    def __init__(self, access_token, camera):
        self.wname = 'video'
        cv2.namedWindow(self.wname, cv2.WINDOW_NORMAL)

        camera_id = camera['id']
        self.alerts = get_camera_alerts(access_token, camera_id)

        pass

    def draw_object(self, frame, obj):
        rect = obj.get_rect()
        cv2.rectangle(frame, rect[0], rect[1], self.bbox_color, 2)
        #print(rect, rect[0], rect[1])
        #cv2.rectangle(frame, (10,10), (100,100), self.bbox_color, 2)

    def draw_zone_VW(self, frame, points):
        color = (0,0,255)
        p1 = points[0]
        p2 = points[1]
        c1 = (p1 + p2) * 0.5
        n = p1 - p2
        cv2.line(frame, tuple(p1), tuple(p2), color, 1)
        pass

    def draw_zone_LD(self, frame, points):
        colorFg = (255,0,0)
        colorBg = (255,128,128)
        #cv2.fillPoly(frame, [points], colorBg)
        cv2.polylines(frame, [points], True, colorFg, 1)
        pass
        
    def draw_zone_RA(self, frame, points):
        colorFg = (0,255,0)
        colorBg = (128,255,128)
        #cv2.fillPoly(frame, [points], color)
        cv2.polylines(frame, [points], True, colorFg, 1)
        pass

    def draw_zones(self, frame):

        h, w = frame.shape[:2]

        for alert in self.alerts:

            points = alert['points']
            points = tuple( (int(w*x[0]), int(h*x[1])) for x in points )
            points = np.array(points, np.int32)

            if alert['type'] == 'VW':
                self.draw_zone_VW(frame, points)
            if alert['type'] == 'LD':
                self.draw_zone_LD(frame, points)
            if alert['type'] == 'RA':
                self.draw_zone_RA(frame, points)
      
    def draw_frame(self, frame, objects):
        """
        @return  True for break
        """

        # draw configered alerts
        self.draw_zones(frame)

        # draw tacker state
        for obj in objects.values():
            self.draw_object(frame, obj)

        cv2.imshow(self.wname, frame)
        return cv2.waitKey(20) == 27 # ESC