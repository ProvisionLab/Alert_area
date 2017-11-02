from trk_object import TrackObject
import numpy as np
import math
import cv2

# alert: 
#{ 
#   'id' : str, 
#   'type' : 'RA'|'LD'|'VW', 
#   'points': [[x1,y1],[x2,y2],[x3,y3]],     # [x,y] are relative to frame size
#   'duration' : int,                        # seconds, for type="LD"
#   'direction' : 'B'|'L'|'R',               # for type="VW", both/to_left/to_right
#}


class AnalyzerState(object):
    """
    implements cashed object state
    """

    curr_pos = None     # np.array
    prev_pos = None     # np.array
    
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
    #camera = None
    alerts = None

    frame_w = None
    frame_h = None

    on_alert = lambda alert_id, obj: None

    state = {}

    def __init__(self, alerts):
        self.n = 0

        self.alerts = alerts
        #self.access_token = access_token
        #self.camera = camera
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

    def check_alert_LD(self, alert, obj: TrackObject, objs: AnalyzerState):
        #points = alert['points']
        #points = tuple( (int(w*x[0]), int(h*x[1])) for x in points )
        pass

    def check_alert_RA(self, alert, obj: TrackObject, objs: AnalyzerState):
        
        if objs.curr_pos is None:
            return

        points = np.array([ (self.frame_w*x[0], self.frame_h*x[1]) for x in alert['points']], np.int32)
        isInside = cv2.pointPolygonTest(points, objs.curr_pos, False)

        #print("inside: ", isInside)

        if isInside <= 0:
            return

        if objs.prev_pos is not None and cv2.pointPolygonTest(points, objs.prev_pos, False) > 0:
            return
            
        self.on_alert(alert['id'], obj)      
        pass

    def set_frame_size(self, w:int, h: int):
        self.frame_w = w
        self.frame_h = h

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

        if (self.n % 60) == 0:
            #camera_id = self.camera['id']
            alert_id = self.alerts[0]['id']
            if self.on_alert:
                #self.on_alert(alert_id, obj)
                pass
            #post_reco_alert(self.access_token, camera_id, alert_id)

        self.n += 1

        # update alerts
        #if (self.n % 60*20) == 0:
        #    self.alerts = get_camera_alerts(self.access_token, self.camera['id'])

        pass

    pass
