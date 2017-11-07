

class TrackObject(object):

    id = None
    pos_x = None
    pos_y = None

    direction = None # move direction, degrees, ccw, 0 - up

    def __init__(self, id: int, x: int, y: int, w: int, h: int):

        self.id = id
        self.pos_x = x
        self.pos_y = y

        self.x1 = x - w/2
        self.x2 = x + w/2
        self.y1 = y - h
        self.y2 = y
        pass

    def get_rect(self):
        return ((int(self.x1), int(self.y1)), (int(self.x2), int(self.y2)))

    def get_pos(self):
        return int(self.pos_x), int(self.pos_y)

    def get_pos_rect(self):
        y1 = self.y2 - (self.y2-self.y1) * 0.3
        return ((int(self.x1), int(y1)), (int(self.x2), int(self.y2)))

    def set_pos(self, x, y):

        w = self.x2 - self.x1
        h = self.y2 - self.y1

        self.pos_x = x
        self.pos_y = y

        self.x1 = x - w/2
        self.x2 = x + w/2
        self.y1 = y - h
        self.y2 = y

    def move(self, dx, dy):

        self.x1 += dx
        self.x2 += dx
        self.pos_x += dx

        self.y1 += dy
        self.y2 += dy
        self.pos_y += dy

    def rect_centre(self):
        return int((self.x1+self.x2)/2), int((self.y1+self.y2)/2)

    pass
