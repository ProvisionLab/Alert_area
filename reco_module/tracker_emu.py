from trk_analyzer import TrackAnalyzer
from trk_object import TrackObject
import random
import math

class TrackerEmu(object):

    frame_w = 1
    frame_h = 1
    objects = {}

    rect_size = 3   # % of frame size
    max_speed = 0.08 # part of rect_size
    dir_sigma = 2.5

    def __init__(self, access_token, camera):

        self.next_id = 0
        self.analyzer = TrackAnalyzer(access_token, camera)
        pass

    def create_object(self):
        w = int(self.frame_w * self.rect_size * 0.01)
        h = int(self.frame_h * self.rect_size * 0.03)
        x = int(random.uniform(0, self.frame_w - w))
        y = int(random.uniform(0, self.frame_h - h))
        obj = TrackObject(self.next_id, x, y, w, h)
        self.objects[self.next_id] = obj
        self.next_id = (self.next_id+1) % 1000

    def delete_some_object(self):

        if len(self.objects) > 0:
            obj_id = random.choice(list(self.objects.keys()))
            del self.objects[obj_id]
        pass

    def delete_object(self, obj: TrackObject):
        del self.objects[obj.id]

    def move_object(self, obj: TrackObject):

        mspd = self.max_speed * self.rect_size * self.frame_w * 0.01
        d = random.uniform(0, mspd)

        if obj.direction is None:
            obj.direction = random.uniform(0, 360)

        dd = random.gauss(0, self.dir_sigma * d)
        if dd < -180: dd = -180
        if dd > 180: dd = 180
        obj.direction += dd

        rdir = obj.direction * math.pi / 180
        dy = - d * math.cos(rdir)
        dx = - d * math.sin(rdir)

        obj.move(dx, dy)

        cx, cy = obj.rect_centre()
        if cx < 0 or cx > self.frame_w or cy < 0 or cy > self.frame_h:
            self.delete_object(obj)

        pass

    def process_frame(self, frame):

        self.frame_h, self.frame_w = frame.shape[:2]

        n1 = int(random.uniform(0, 50))

        if (n1 == 1 and len(self.objects) < 1) or (n1 == 2 and len(self.objects) < 4):
            self.create_object()

        if n1 == 9 and len(self.objects) > 4:
            self.delete_some_object()

        for obj in list(self.objects.values()):
            self.move_object(obj)

        self.analyzer.process_object(None)
        pass
