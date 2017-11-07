from trk_object import TrackObject
import random
import math


dbg_object_id = 10000

class TrackerEmu(object):

    frame_w = 1
    frame_h = 1
    objects = None

    rect_size = 3   # % of frame size
    max_speed = 0.08 # part of rect_size
    dir_sigma = 100

    def __init__(self):

        self.objects = {}
        self.next_id = 0
        pass

    def create_object(self):
        h = int(self.frame_h * self.rect_size * 0.03)

        x = int(random.uniform(0, self.frame_w))
        y = int(random.uniform(h, self.frame_h))

        self.create_object_at(self.next_id, x, y)
        self.next_id = (self.next_id+1) % 1000

    def create_dbg_object(self, x, y):
        self.create_object_at(dbg_object_id, x, y)
        pass

    def remove_dbg_object(self):
        self.objects.pop(dbg_object_id, None)
        pass

    def move_dbg_object(self, x, y):
        obj = self.objects.get(dbg_object_id)
        if obj: 
            obj.set_pos(x, y)
        pass

    def delete_some_object(self):

        if len(self.objects) > 0:
            obj_id = random.choice(list(self.objects.keys()))
            if obj_id != dbg_object_id:
                del self.objects[obj_id]
        pass

    def create_object_at(self, id, x, y):
        w = int(self.frame_w * self.rect_size * 0.01)
        h = int(self.frame_h * self.rect_size * 0.03)

        obj = TrackObject(id, x, y, w, h)

        self.objects[id] = obj
        pass

    def delete_object(self, obj: TrackObject):
        del self.objects[obj.id]

    def move_object(self, obj: TrackObject):

        mspd = random.uniform(0, self.max_speed)

        if obj.direction is None:
            obj.direction = random.uniform(0, 360)

        dd = random.gauss(0, self.dir_sigma * mspd)
        if dd < -180: dd = -180
        if dd > 180: dd = 180
        obj.direction += dd

        d = mspd * self.rect_size * self.frame_w * 0.01

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

        #if (n1 == 1 and len(self.objects) < 1) or (n1 == 2 and len(self.objects) < 4):
        #    self.create_object()

        if n1 == 9 and len(self.objects) > 4:
            self.delete_some_object()

        for obj in list(self.objects.values()):
            if obj.id != dbg_object_id:
                self.move_object(obj)

        pass
