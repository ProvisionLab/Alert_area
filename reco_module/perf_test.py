#!/usr/bin/python3

import sys, argparse, time, signal
import logging, logging.config
from capture_worker import CaptureWorker

#STREAM_1080_URL = 'rtsp://admin:admin@47.40.34.31:554' # 1920 x 1080
#STREAM_1080_URL = 'rtsp://admin:admin@23.243.152.142:554' # 1920 x 1080
STREAM_1080_URL = 'rtsp://admin:admin@207.62.193.8:8554' # 1920 x 1080
#STREAM_1080_URL = 'rtsp://admin:admin@12.110.253.194:554'

#STREAM_720_URL = 'rtsp://admin:123456@219.85.200.55:554' # 1280 x 720
STREAM_720_URL = 'rtsp://admin:admin@14.45.88.220:554' # 1280 x 720
STREAM_576_URL = 'rtsp://admin:admin@217.73.179.4:554' # 960 x 576
STREAM_480_URL = 'rtsp://admin:123456@121.254.64.108:554' # 960 x 480
STREAM_240_URL = 'rtsp://admin:admin@190.63.185.42:554' # 704 x 240



logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detail': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class':'logging.StreamHandler',
            'formatter' : 'simple',
        },
    },

    'loggers': {
        'paramiko': {
            'level': 'ERROR',
        },
        'requests.packages.urllib3.connectionpool' : {
            'level': 'ERROR',
        },
    },

    'root': {
        'level': 'ERROR',
        'handlers': ['console'],
    }
})

class App(object):
    
    def __init__(self):

        self.bStop = False
        self.capture_workers = []

        signal.signal(signal.SIGINT, self.stop_execution)
        pass

    def add_worker(self, id: int, url: str):
        print('add_worker: ', url)

        worker = CaptureWorker(camera={'id': id, 'name': '', 'url': url}, connection=None)
        worker.restart_on_fail = True
        worker.use_motion_detector = False
        self.capture_workers.append(worker)

        pass

    def stop_execution(self, signum, taskfrm):
        """
        SIGINT handler
        """
        print('Ctrl+C was pressed')
        self.bStop = True

        for t in self.capture_workers:
            t.stop()

    def run(self):
        
        for w in self.capture_workers:
            w.start()

        print()

        while not self.bStop:
            
            try:

                now = time.time()

                total_fps1 = 0.0
                total_fps2 = 0.0
                cameras_count = 0
                
                for t in self.capture_workers:
                    fps1, fps2 = t.get_fps()
                    total_fps1 += fps1
                    total_fps2 += fps2
                    if fps1 > 0:
                        cameras_count +=1

                avg_fps1 = total_fps1 / cameras_count if cameras_count > 0 else 0.0
                avg_fps2 = total_fps2 / cameras_count if cameras_count > 0 else 0.0

                print("total input fps: {:.2f}, total reco fps: {:.2f}, cameras: {}, average fps: input: {:.2f}, reco: {:.2f}".format(
                    total_fps1, total_fps2, 
                    cameras_count,
                    avg_fps1, avg_fps2))

            except Exception as e:

                print(str(e))
                pass

            time.sleep(5.0)

        for t in self.capture_workers:
            t.join()

        print("Quit")
        pass

def main(argv):
    
    try:

        parser = argparse.ArgumentParser(description='perfomance test.')

        parser.add_argument('--size', '-s', type=int, default=1080, help='frame size: 1080, 720, 480')
        parser.add_argument('--count', '-n', type=int, default=1, help='feeds count')
        parser.add_argument('--source', nargs='?', help='video source url')

        args = parser.parse_args(argv[1:])

    except Exception as e:
        print(e)
        return

    url = args.source
    if url is None:
        
        fsize = args.size

        if fsize == 1080:
            url = STREAM_1080_URL

        elif fsize == 720:
            url = STREAM_720_URL

        elif fsize == 480:
            url = STREAM_480_URL

        else:
            print('error: no source stream defined')
            return

    app = App()

    for i in range(0, args.count):
        app.add_worker(i,url)

    app.run()
    pass

if __name__ == "__main__":

    main(argv=sys.argv)
    #main(argv=[""])
    #main(argv=["","-s", "480", "-n", "4"])
    #main(argv=["","-s", "720", "-n", "4"])
    #main(argv=["","-s", "1080", "-n", "1"])
    #main(argv=["", "-n", "4", "--source=rtsp://admin:admin@190.63.185.42:554"])
    #main(argv=["", "-n", "1", "--source=rtsp://admin:admin@12.110.253.194:554"])
    #main(argv=["", "-n", "1", "--source=rtsp://12.110.253.194:554"])
