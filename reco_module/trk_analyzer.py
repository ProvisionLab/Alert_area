from trk_object import TrackObject
from reco_client import post_reco_alert, get_camera_alerts

# alert: 
#{ 
#   'id' : str, 
#   'type' : 'RA'|'LD'|'VW', 
#   'points': [[x1,y1],[x2,y2],[x3,y3]],     # [x,y] are relative to frame size
#   'duration' : int,                        # seconds, for type="LD"
#   'direction' : 'B'|'L'|'R',               # for type="VW", both/to_left/to_right
#}


class TrackAnalyzer(object):
    """
    analizer for person tracker
    """

    access_token = None
    camera = None
    alerts = None

    def __init__(self, access_token, camera):
        self.n = 0
        self.access_token = access_token
        self.camera = camera

        camera_id = self.camera['id']
        self.alerts = get_camera_alerts(access_token, camera_id)
        pass

    def process_object(self, obj: TrackObject):
        """
        analyze object from current frame
        """

        if (self.n % 60) == 0:
            camera_id = self.camera['id']
            alert_id = self.alerts[0]['id']
            #post_reco_alert(self.access_token, camera_id, alert_id)

        self.n += 1

        # update alerts
        if (self.n % 60*20) == 0:
            self.alerts = get_camera_alerts(self.access_token, self.camera['id'])

        pass

    pass
