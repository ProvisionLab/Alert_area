"""
main module
"""
import os, time, signal, sys, argparse
import multiprocessing
import uuid
import requests, requests.utils
from capture_worker import CaptureWorker
from alert_object import AlertObject, set_alert_type_ids
import reco_config
from collections import deque

from rogapi import ROG_Client
from rogapi.alerts import ROG_Alert, ROG_AlertImage

import reco_logging, logging

from bvcapi import BVC_Client

class RecoApp(object):
    
    alerts = None

    bStop = False

    use_cpu = reco_config.use_cpu

    def __init__(self, reco_num: int, reco_count: int):
        
        self.reco_num = reco_num

        self.reco_id = '{}:{}'.format(reco_config.reco_name, self.reco_num)

        self.reco_count = reco_count

        self.threads = []
        self.alerts_queue = deque()
        self.thumbnail_queue = deque()

        self.bvcapi = BVC_Client(reco_config.bvcapi_url, 'reco-' + self.reco_id, reco_config.bvcapi_key)
        self.bvcapi.session.verify = reco_config.bvcapi_verify_ssl
        
        self.rogapi = ROG_Client(reco_config.rogapi_url, reco_config.rogapi_username, reco_config.rogapi_password)

        signal.signal(signal.SIGINT, self.stop_execution)
        signal.signal(signal.SIGTERM, self.on_sigterm)
        pass

    def stop(self):

        self.bStop = True

        if len(self.alerts_queue)>4:
            logging.warning("there are many alerts in queue: %d, reseting them", len(self.alerts_queue))
            self.alerts_queue.clear()
        
        for t in self.threads:
            t.stop()

    def on_sigterm(self, signum, taskfrm):
        
        logging.info("reco proc: SIGTERM reseived")

        self.stop()

    def stop_execution(self, signum, taskfrm):
        """
        SIGINT handler
        """
        print('Ctrl+C was pressed')

        logging.info("SIGINT reseived, stop all recognitions")

        self.stop()

    def run(self):
        """
        main loop
        periodically reads config state from backend
        starts/stops recognition threads
        """

        #logging.info("reco start")
        #while not self.bStop:
        #    time.sleep(5)
        #logging.info("reco exit")
        #return

        try:

            set_alert_type_ids(self.rogapi.get_alert_ids())

            self.updatate_timer = 0

            while not self.bStop:
                
                try:

                    now = time.time()

                    if (now - self.updatate_timer) >= reco_config.update_interval:

                        self.update_cameras()

                        self.updatate_timer = now

                    if self.alerts_queue or self.thumbnail_queue:

                        self.post_all_alerts()
                        self.post_all_thumbnails()

                    else:
                        time.sleep(2.0)

                except (requests.exceptions.ConnectionError) as e:

                    logging.error("ConnectionError: %s", str(e))
                    time.sleep(30)
                    pass

                except (requests.exceptions.HTTPError) as e:

                    logging.error("HTTPError: %s", str(e))
                    time.sleep(30)
                    pass

                except (Exception) as e:

                    logging.exception("exception")
                    time.sleep(30)
                    pass


        except:

            logging.exception("exception")
            pass                    

        logging.info("stopping... this may take some time")

        for t in self.threads:
            t.stop()

        for t in self.threads:
            t.join()

        self.bvcapi.post_reco_end()

        logging.info("RecoApp %d: Quit", self.reco_num)

    def update_cameras(self):
        """
        gets cameras from backend
        updates recognizers
        """

        status = self.get_status()

        self.bvcapi.post_status(status)

        cameras = self.bvcapi.get_active_cameras()

        if cameras is None:
            raise Exception("backend cameras request failed, no cameras returned")

        self.set_cameras(cameras)

    def remove_stoped_threads(self):

        del_threads = [t for t in self.threads if t.bExit]        
        self.threads = [t for t in self.threads if not t.bExit]

        for t in del_threads:
            t.join()

    def get_status(self):
        
        total_fps1 = 0.0
        total_fps2 = 0.0

        cameras = []

        stat = []
        
        for t in self.threads:

            tstat = t.get_stat()
            stat.append( tstat )

            interval = tstat.get('interval',0)
            freq = 1000.0 / interval if interval > 0 else 0.0

            fps1 = tstat.get('capture',0) * freq
            fps2 = tstat.get('analyze',0) * freq

            total_fps1 += fps1
            total_fps2 += fps2

            logging.info("FPS: %.1f/%.1f", fps1, fps2)

            cameras.append({
                'id' : t.camera.get('id'),
                'fps1' : fps1,
                'fps2' : fps2,
            })

            logging.info("camera [%d] \'%s\' FPS: %.1f/%.1f, areas: %d, users: %s", 
                        t.camera['id'], t.camera['name'], 
                        fps1, fps2, 
                        len(t.camera.get('areas',[])),
                        str(t.camera.get('users',[])))

        logging.info("total FPS: %.1f/%.2f for %d cameras", total_fps1, total_fps2, len(cameras))

        return {'status': stat, 'cameras' : cameras, 'fps' : total_fps2}

    def set_cameras(self, cameras):
        """
        sets cameras for recognition
        stops/starts recognition
        updates alert areas of recognizers
        """
        
        # remove stoped threads
        self.remove_stoped_threads()

        # filter cameras by reco_num
        #cameras = [c for c in cameras if (c['id'] % self.reco_count) == self.reco_num]

        # get new cameras alerts
        for c in cameras:
            #logging.info("camera [%d] %s", c['id'], str(c))
            #areas = self.bvcapi.get_camera_alerts(c['id'])
            #c['areas'] = areas;
            areas = c.get('alerts')
            if not areas:
                logging.warning("camera [%d] \'%s\' has no alerts configured, users: %s", 
                    c['id'], c['name'], str(c.get('users',[])))

        # remove cameras with no alert areas
        #cameras = [c for c in cameras if c['areas']]

        #
        old_cameras = [t.camera for t in self.threads]

        old_ids = [c['id'] for c in old_cameras]
        new_ids = [c['id'] for c in cameras]
        del_ids = [c['id'] for c in old_cameras if c.get('id') not in new_ids]

        # delete cameras

        del_threads = [t for t in self.threads if t.camera['id'] in del_ids]
        new_threads = [t for t in self.threads if t.camera['id'] not in del_ids]

        for t in del_threads:
            logging.info("stop recognition of camera: [%d] \'%s\'", t.camera['id'], t.camera['name'])
            t.stop()

        self.threads = new_threads

        # update alert areas
        for t in self.threads:
            camera_id = t.camera['id']
            for c in cameras:
                if c['id'] == camera_id:
                    t.update_camera(c)

        # add new camera threads
        add_cameras = [c for c in cameras if c['id'] not in del_ids and c['id'] not in old_ids]

        for c in add_cameras:
            logging.info("start recognition of camera: [%d] \'%s\', users: %s", c['id'], c['name'], str(c.get('users',[])))

            t = CaptureWorker(self, c)
            t.use_cpu = self.use_cpu

            self.threads.append(t)
            t.start()
            
        self.cameras = cameras
        pass


    def post_reco_alert(self, alert: AlertObject):
        """
        appends alert to alerts queue
        """

        self.alerts_queue.append(alert)

    def post_thumbnail(self, camera_id:int, image:str, timestamp:str, user_id=None):
        logging.warning('post_thumbnail of camera [%d], user: %d', camera_id, user_id)
        self.thumbnail_queue.append(
            {
            'camera_id' :camera_id, 
            'image'     :image, 
            'timestamp' :timestamp, 
            'user_id'   :user_id
            })

    def post_connection_fail(self, camera_id:int, user_id=None):
        logging.warning('post_connection_fail of camera [%d], user: %d', camera_id, user_id)
        self.thumbnail_queue.append({'camera_id':camera_id, 'user_id':user_id})

    def post_all_alerts(self):
        """
        posts all alerts from queue
        """

        if len(self.alerts_queue) > reco_config.max_alert_queue_size:
            logging.warning('alerts queue too long (%d), droping', len(self.alerts_queue))
            self.alerts_queue = deque(self.alerts_queue, reco_config.max_alert_queue_size)

        start_time = time.time()

        while self.alerts_queue:
            
            alert = self.alerts_queue.popleft()

            try:

                if reco_config.send_alerts_to_rog:

                    if isinstance(alert, ROG_Alert):

                        rog_alert_id = self.rogapi.post_alert(alert.get_data())

                        if rog_alert_id:
                            logging.info("alert [%d] is send: %s, %d left", alert.camera_id, rog_alert_id, len(self.alerts_queue))
                        else:
                            logging.warning("alert [%d] not sent, %d left", alert.camera_id, len(self.alerts_queue))

                        if rog_alert_id and alert.obj:
                            alert.obj.rog_alert_id = rog_alert_id
                    
                    elif isinstance(alert, ROG_AlertImage):
                        

                        if alert.obj:
                            alert.rog_alert_id = alert.obj.rog_alert_id

                        if alert.rog_alert_id:
                            self.rogapi.add_alert_image(alert.rog_alert_id, alert.image.get_data())
                        else:
                            logging.warning("alert TA id not defined, %s", alert.alert_id)

                    else:
                        
                        logging.warning("invalid alert type: %s", type(alert))
                        pass
       
                else:
                    self.bvcapi.post_alert(alert)

            except:
                logging.exception("exception in rogapi.add_alert_image")
                pass
                    

            if (time.time() - start_time) > 10.0:
                break;

            if self.bStop:
                break

    def post_all_thumbnails(self):
        """
        posts all thumbnails from queue
        """

        if len(self.thumbnail_queue) > reco_config.max_alert_queue_size:
            logging.warning('thumbnail_queue queue too long (%d), droping', len(self.thumbnail_queue))
            self.thumbnail_queue = deque(self.thumbnail_queue, reco_config.max_alert_queue_size)

        start_time = time.time()

        while not self.bStop and self.thumbnail_queue:
            
            thumbnail = self.thumbnail_queue.popleft()
            camera_id = thumbnail.get('camera_id')
            user_id = thumbnail.get('user_id')

            try:

                if thumbnail.get('image'):
                    self.bvcapi.post_thumbnail(thumbnail)
                else:
                    self.bvcapi.post_connectionFail(camera_id)

            except:
                logging.exception("exception in bvcapi.post_thumbnail")
                pass

            try:

                if thumbnail.get('image'):
                    self.rogapi.remote_camera_image(thumbnail)
                else:
                    self.rogapi.post_connection_fail(camera_id, user_id=user_id)

            except:
                logging.exception("exception in rogapi.remote_camera_image")
                pass
                
                    
            if (time.time() - start_time) > 10.0:
                break;

def get_user_agent(name="BVC reco_module"):
    return name

pid = None
pid_fname = None

def main(reco_num, reco_count):
    
    pid = str(os.getpid())
    pid_fname = 'reco_proc_'+str(reco_num)+'.pid'
    f = open(pid_fname, 'w')
    f.write(pid)
    f.close()

    app = RecoApp(reco_num, reco_count)
    #app.use_cpu = reco_count > 1 and reco_num == reco_count
    app.run()
    
    os.remove(pid_fname)
    exit(1)

class RecoPool(object):

    def __init__(self, reco_count):
        
        self.reco_count = reco_count
        self.pool = multiprocessing.Pool(reco_count)

        signal.signal(signal.SIGINT, self._sigint_handler)
        signal.signal(signal.SIGTERM, self._sigterm_handler)

    def run2(self):
        
        args = zip(range(0,self.reco_count), [self.reco_count]*self.reco_count)

        with self.pool:
            res = self.pool.starmap(main, args)
            print(res)

    def run(self):
        
        args = zip(range(0,self.reco_count), [self.reco_count]*self.reco_count)

        try:
            res = self.pool.starmap_async(main, args)
            # wait results
            res = res.get()

        except KeyboardInterrupt:
            #print("Caught KeyboardInterrupt, terminating workers")
            #logging.warning("Caught KeyboardInterrupt")
            self.pool.terminate()

        except Exception as e:
            #print(e)
            #logging.warning("%s", str(e))
            self.pool.terminate()

        else:
            #print("Normal termination 2")
            #logging.warning("Normal termination")
            #print(res)
            pass

        finally:
            #print("finally")
            #logging.warning("finally")
            self.pool.close()
            self.pool.join()

        #print("main exit")
        logging.warning("reco_main exit")

    def _sigint_handler(self, signum, taskfrm):

        logging.warning("reco_main SIGINT received")
        self.pool.terminate()
        self.pool.close()
        self.pool.join()
        sys.exit(1)

    def _sigterm_handler(self, signum, taskfrm):
    
        logging.warning("reco_main SIGTERM received")
        self.pool.terminate()
        self.pool.close()
        self.pool.join()
        sys.exit(1)

if __name__ == '__main__':
    
    # parse arguments

    parser = argparse.ArgumentParser(description='reco module.')
    parser.add_argument('--workers', '-w', type=int, default=1, help='workers count')

    args = parser.parse_args(sys.argv[1:])

    reco_count = args.workers

    requests.utils.default_user_agent = get_user_agent

    pid = str(os.getpid())
    pid_fname = 'reco.pid'
    f = open(pid_fname, 'w')
    f.write(pid)
    f.close()

    pool = RecoPool(reco_count)
    pool.run()

    os.remove(pid_fname)
