from trk_object import TrackObject
import numpy as np
import math
import cv2
import time

# alert: 
#{ 
#   'id' : str, 
#   'type' : 'RA'|'LD'|'VW', 
#   'points': [[x1,y1],[x2,y2],[x3,y3]],     # [x,y] are relative to frame size
#   'duration' : int,                        # seconds, for type="LD"
#   'direction' : 'B'|'L'|'R',               # for type="VW", both/to_left/to_right
#}

DEBUG = True

class AnalyzerState(object):
    """
    implements cashed object state
    """

    curr_pos = None     # np.array
    prev_pos = None     # np.array

    duration = None     # time of "enter" event
    
    def __init__(self):
        pass

    def is_outdated(self):
        return self.curr_pos is None

    def begin_frame(self):
        self.prev_pos = self.curr_pos
        self.curr_pos = None

    def update(self, obj):
        self.curr_pos = (obj.pos_x, obj.pos_y)

    def end_frame(self, obj):
        pass

class TrackAnalyzer(object):
    """
    analizer for person tracker
    """

    access_token = None
    alerts = None

    frame_w = None
    frame_h = None

    on_alert = lambda alert_id, obj: None

    state = {}

    def __init__(self, alerts):

        self.alerts = alerts

        if DEBUG:
            for alert in self.alerts:
                if alert['type'] == 'LD':
                    alert['duration'] = 5
        pass

    def process_objects(self, w:int, h:int, objects):

        # prepare cash
        for s in self.state.values():
            s.begin_frame()

        self.set_frame_size(w, h)

        for obj in objects:
            objs = self.state.get(obj.id);
            if objs is None:
                objs = AnalyzerState()
                self.state[obj.id] = objs
            
            objs.update(obj)
           
            self.process_object(obj, objs)
        
        # remove outdated cash
        self.state = { k:s for k,s in self.state.items() if not s.is_outdated() }

    #############################################################################

    def set_frame_size(self, w:int, h: int):
        self.frame_w = w
        self.frame_h = h

    def check_alert_VW(self, alert, obj: TrackObject, objs: AnalyzerState):
        
        if objs.curr_pos is None or objs.prev_pos is None:
            return

        points = [ (self.frame_w*x[0], self.frame_h*x[1]) for x in alert['points']]
        p1 = np.array(points[0])
        p2 = np.array(points[1])

        vv = p2-p1
        VV = np.linalg.norm(vv)

        # do not alert if wall is less 1 px length
        if VV < 1.0:
            return
        
        vp = np.array(objs.prev_pos) - p1
        vc = np.array(objs.curr_pos) - p1

        px = np.dot(vp, vv) / VV
        py = np.cross(vp, vv) / VV
        
        cx = np.dot(vc, vv) / VV
        cy = np.cross(vc, vv) / VV

        if py * cy >= 0:
            # no crossing
            return

        cpx = cx-px
        cpy = cy-py

        if math.fabs(cpy) > 1.0: 
            xx = (px * cpy - py * cpx) / cpy
        else:
            xx = (px + cx) * 0.5

        if xx < 0 or xx > VV:
            # no wall crossing
            return

        cross_L = cy > 0 and py < 0
        cross_R = cy < 0 and py > 0

        direction = alert['direction']

        if direction == 'B' or (cross_L and direction == 'L') or (cross_R and direction == 'R'):
            self.on_alert(alert['id'], obj)      
        pass

    def check_alert_RA(self, alert, obj: TrackObject, objs: AnalyzerState):
        if self.check_area_enter(alert, objs) == 1: # enter
            self.on_alert(alert['id'], obj)

    def check_alert_LD(self, alert, obj: TrackObject, objs: AnalyzerState):
        
        res = self.check_area_enter(alert, objs)
        if res == 1:
            # enter area
            objs.duration = time.time()
        elif res == 2:
            # leave area
            objs.duration = None
        elif objs.duration is not None:
            # inside area
            delta = time.time() - objs.duration
            if delta >= alert['duration']:
                objs.duration = None
                self.on_alert(alert['id'], obj)
        pass

    def process_object(self, obj: TrackObject, objs: AnalyzerState):
        """
        analyze object from current frame
        """

        for alert in self.alerts:

            if alert['type'] == 'VW':
                self.check_alert_VW(alert, obj, objs)
            elif alert['type'] == 'LD':
                self.check_alert_LD(alert, obj, objs)
            elif alert['type'] == 'RA':
                self.check_alert_RA(alert, obj, objs)

        pass

    def check_area_enter(self, alert: dict, objs: AnalyzerState):
        """
        @return 0 - no event, 1 - enter, 2 - leave
        """
        if objs.curr_pos is None:
            return 0

        points = np.array([ (self.frame_w*x[0], self.frame_h*x[1]) for x in alert['points']], np.int32)
        res = cv2.pointPolygonTest(points, objs.curr_pos, False)

        res_prev = cv2.pointPolygonTest(points, objs.prev_pos, False) if objs.prev_pos is not None else None

        if res > 0:
            if res_prev is None or res_prev <= 0:
                return 1 # enter
        else:
            if res_prev is not None and res_prev > 0:
                return 2 # leave
            
        return 0
