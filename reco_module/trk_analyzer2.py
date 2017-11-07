from trk_object import TrackObject
import numpy as np
import math
import cv2
import time
import reco_config

# alert: 
#{ 
#   'id' : str, 
#   'type' : 'RA'|'LD'|'VW', 
#   'points': [[x1,y1],[x2,y2],[x3,y3]],     # [x,y] are relative to frame size
#   'duration' : int,                        # seconds, for type="LD"
#   'direction' : 'B'|'L'|'R',               # for type="VW", both/to_left/to_right
#}


leave_timer_duration = 2 # second

class AreaState(object):
    """
    """

    id = None
    type = None
    points = []
    duration = None
    direction = None

    timer1 = None     # time of "enter" event
    timer2 = None     # time of "leave" event
    
    def __init__(self, params: dict):
        self.id = params['id']    
        self.type = params['type']
        self.points = params['points']
        self.duration = params.get('duration', None)
        self.direction = params.get('direction', None)
        pass

    def get_pos(self):
        x = 0
        y = 0
        n = len(self.points)
        for p in self.points:
            x += p[0]
            y += p[1]

        return x/n, y/n


class TrackAnalyzer2(object):
    """
    analizer for person tracker
    """

    access_token = None
    alert_areas = None

    frame_w = None
    frame_h = None

    on_alert = lambda alert_id, obj: None

    def __init__(self, alert_areas):

        self.alert_areas = [AreaState(a) for a in alert_areas]

        if reco_config.DEBUG:
            for alert_area in self.alert_areas:
                if alert_area.type == 'LD':
                    alert_area.duration = 5
        pass

    def process_objects(self, w: int, h: int, objects):

        self.set_frame_size(w, h)

        for area in self.alert_areas:
            self.process_area(area, objects)

    #############################################################################

    def set_frame_size(self, w:int, h: int):
        self.frame_w = w
        self.frame_h = h

    def process_area(self, area, objects):
        
        if area.type == 'VW':
            self.check_area_VW(area, objects)
        elif area.type == 'LD':
            self.check_area_LD(area, objects)
        elif area.type == 'RA':
            self.check_area_RA(area, objects)

        pass

    def on_area_enter(self, area):
        pos = area.get_pos()
        pos = (int(pos[0] * self.frame_w), int(pos[1] * self.frame_h))
        self.on_alert(area.id, True, pos)
        pass

    def on_area_leave(self, area):
        pos = area.get_pos()
        pos = (int(pos[0] * self.frame_w), int(pos[1] * self.frame_h))
        self.on_alert(area.id, False, pos)
        pass

    def check_area_RA(self, area, objects):
        
        area_empty = True
        for o in objects:
            if self.area_contains_object(area, o):
                area_empty = False
                break

        if (area.timer1 is None) and not area_empty:
            # enter event
            area.timer1 = time.time()
            area.timer2 = None
            self.on_area_enter(area)
            pass

        elif (area.timer1 is not None) and area_empty:
            # leave event
            area.timer1 = None
            area.timer2 = time.time()
            pass

        if (area.timer1 is None) and (area.timer2 is not None):
            delta = time.time() - area.timer2
            if delta >= leave_timer_duration:
                area.timer2 = None
                self.on_area_leave(area)

        pass

    def check_area_LD(self, area, objects):
        
        area_empty = True
        for o in objects:
            if self.area_contains_object(area, o):
                area_empty = False
                break

        if (area.timer1 is None) and not area_empty:
            # enter event
            area.timer1 = time.time()
            area.timer2 = None
            area.LD_enter = False
            pass

        elif (area.timer1 is not None) and area_empty:
            # leave event
            area.timer1 = None
            if area.LD_enter:
                area.timer2 = time.time()
            else:
                area.timer2 = None
            pass

        if (area.timer1 is not None) and not area.LD_enter:
            delta = time.time() - area.timer1
            if delta >= area.duration:
                area.LD_enter = True
                self.on_area_enter(area)

        if (area.timer1 is None) and (area.timer2 is not None):
            delta = time.time() - area.timer2
            if delta >= leave_timer_duration:
                area.timer2 = None
                self.on_area_leave(area)

        pass

    def check_area_VW(self, area, objects):
        
        points = [(self.frame_w*x[0], self.frame_h*x[1]) for x in area.points]
        p1 = np.array(points[0])
        p2 = np.array(points[1])

        area_empty = True
        for o in objects:
            if self.line_cross_object(p1, p2, o):
                area_empty = False
                break

        if (area.timer1 is None) and not area_empty:
            # enter event
            area.timer1 = time.time()
            area.timer2 = None
            self.on_area_enter(area)
            pass

        elif (area.timer1 is not None) and area_empty:
            # leave event
            area.timer1 = None
            area.timer2 = time.time()
            pass

        if (area.timer1 is None) and (area.timer2 is not None):
            delta = time.time() - area.timer2
            if delta >= leave_timer_duration:
                area.timer2 = None
                self.on_area_leave(area)

        pass

    def get_point_line_distance2(self, p, p1, p2):
        vv = p2-p1
        VV = np.linalg.norm(vv)
        if VV < 1.0:
            d = p - p1
            return np.linalg.norm(d)

        vp = p - p1
        py = np.cross(vp, vv) / VV

        return py

    def rect_contains_point(self, rect, p):
        return rect[0][0] <= p[0] and rect[1][0] >= p[0] and rect[0][1] <= p[1] and rect[1][1] >= p[1]

    def line_cross_object(self, p1, p2, obj: TrackObject):
        
        pos_rect = obj.get_pos_rect()

        pr = [
            np.array((pos_rect[0][0], pos_rect[0][1])),
            np.array((pos_rect[0][0], pos_rect[1][1])),
            np.array((pos_rect[1][0], pos_rect[1][1])),
            np.array((pos_rect[1][0], pos_rect[0][1]))
        ]

        n_left = 0
        n_right = 0
        for p in pr:
            d = self.get_point_line_distance2(p, p1, p2)
            if d >= 0: 
                n_left += 1
            else:
                n_right += 1

        if n_left == 0 or n_right == 0:
            # no crossing
            return False

        if self.rect_contains_point(pos_rect, p1) or self.rect_contains_point(pos_rect, p2):
            return True

        if self.line_cross_line(p1, p2, pr[0], pr[1]):
            return True
        if self.line_cross_line(p1, p2, pr[1], pr[2]):
            return True
        if self.line_cross_line(p1, p2, pr[2], pr[3]):
            return True
        if self.line_cross_line(p1, p2, pr[3], pr[0]):
            return True

        return False

    def line_cross_line(self, p1, p2, b1, b2):
        
        vv = p2-p1
        VV = np.linalg.norm(vv)

        # do not alert if wall is less 1 px length
        if VV < 1.0:
            return False
        
        vp = np.array(b1) - p1
        vc = np.array(b2) - p1

        px = np.dot(vp, vv) / VV
        py = np.cross(vp, vv) / VV
        
        cx = np.dot(vc, vv) / VV
        cy = np.cross(vc, vv) / VV

        if py * cy >= 0:
            # no crossing
            return False

        cpx = cx-px
        cpy = cy-py

        if math.fabs(cpy) > 1.0: 
            xx = (px * cpy - py * cpx) / cpy
        else:
            xx = (px + cx) * 0.5

        if xx < 0 or xx > VV:
            # no wall crossing
            return False

        return True

    def area_contains_object(self, area: AreaState, obj: TrackObject):
        points = np.array([ (self.frame_w*x[0], self.frame_h*x[1]) for x in area.points], np.int32)
        res = cv2.pointPolygonTest(points, obj.get_pos(), False)
        return res > 0
