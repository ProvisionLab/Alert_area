import cv2
import numpy as np
from tracker_emu import TrackerEmu

class DebugWindow:

    bbox_color = (0, 255, 0)

    zones = None

    max_alert_r = 5 # % of w
    alerts = []

    tracker = None

    def __init__(self, camera, tracker, alert_areas):
        
        camera_id = camera['id']

        self.wname = camera['name']
        cv2.namedWindow(self.wname, cv2.WINDOW_AUTOSIZE) #cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.wname, self.on_mouse)

        self.zones = alert_areas

        self.tracker = tracker

        pass

    def close(self):
        cv2.destroyWindow(self.wname)

    def add_alert(self, pos, is_enter: bool = True):
        
        self.alerts.append({'pos':pos, 'is_enter' : is_enter, 'r':0})
        pass

    def draw_frame(self, frame, objects):
        """
        @return  True for break
        """

        # draw configered alerts
        self.draw_zones(frame)

        # draw tracker state
        for obj in objects:
            self.draw_object(frame, obj)

        self.draw_alerts(frame)            

        cv2.imshow(self.wname, frame)
        return cv2.waitKey(20) == 27 # ESC

    def update_areas(self, areas):
        self.zones = areas
        pass

    # private methods        

    def draw_alerts(self, frame):
        
        w = frame.shape[1]

        max_r = w * self.max_alert_r / 100
        max_r2 = max_r / 2

        for alert in self.alerts:
            r = alert['r']
            alert['r'] += 1
            if alert['is_enter']:
                cv2.circle(frame, alert['pos'], r, (255,0,255), 2)
                if r >= max_r:
                    alert['done'] = True
            else:
                r =  int(max_r2 - r)
                if r > 0:
                    cv2.circle(frame, alert['pos'], r, (255,255,0), 2)

                if r <= 0:
                    alert['done'] = True
            pass

        self.alerts = [a for a in self.alerts if not a.get('done', False)]
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

        for alert in self.zones:

            points = alert['points']
            points = tuple( (int(w*x[0]), int(h*x[1])) for x in points )
            points = np.array(points, np.int32)

            if alert['type'] == 'VW':
                self.draw_zone_VW(frame, points)
            if alert['type'] == 'LD':
                self.draw_zone_LD(frame, points)
            if alert['type'] == 'RA':
                self.draw_zone_RA(frame, points)
      
    def on_mouse(self, event, x, y, flags, param):

        if not isinstance(self.tracker, TrackerEmu):
            return

        #print("on_mouse")

        if event == cv2.EVENT_LBUTTONDOWN:
            #print("EVENT_LBUTTONDOWN: {0} {1}".format(x,y))
            self.tracker.create_dbg_object(x,y)

        elif event == cv2.EVENT_LBUTTONUP :
            #print("EVENT_LBUTTONUP: {0} {1}".format(x,y))
            self.tracker.remove_dbg_object()

        elif event == cv2.EVENT_MOUSEMOVE:
            if flags & cv2.EVENT_FLAG_LBUTTON == 0:
                self.tracker.remove_dbg_object()
            else:
                self.tracker.move_dbg_object(x,y)

        pass
