

class TrackObject(object):

    id = None
    pos_x = None
    pos_y = None

    direction = None # move direction, degrees, ccw, 0 - up

    def __init__(self, id: int, x: int, y: int, w: int, h: int):
        self.id = id
        self.x1 = x
        self.x2 = x + w
        self.y1 = y
        self.y2 = y + h
        self.pos_x = (self.x1 + self.x2)/2
        self.pos_y = self.y2
        pass

    def get_rect(self):
        return ((int(self.x1), int(self.y1)), (int(self.x2), int(self.y2)))

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
