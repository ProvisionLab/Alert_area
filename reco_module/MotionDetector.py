import cv2



class MotionDetector:
    
    def __init__(self, min_area):
        self.previous_frame = None
        self.min_area = min_area
    
    def isMotion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.previous_frame is None:
            self.previous_frame = gray
            return True
        
        frameDelta = cv2.absdiff(self.previous_frame, gray)
        self.previous_frame = gray
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        (_, contours, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in contours:
           # if the contour is too small, ignore it
           if cv2.contourArea(c) > self.min_area:
               return True

        return False
