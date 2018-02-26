import time
import bvc_db
import random
from threading import Lock
from threading import Thread

import bvc_logging, logging
log = logging.getLogger('reco_dispatcher')

purge_timeout = 200  # seconds

fix_timeot = 120
not_fixed_fps = 10
fix_window = 300

def split_recoid(reco_id):
    i = reco_id.rfind(':')
    if i >= 0:
        instance_id = reco_id[:i]
        process_id = reco_id[i+1:]
    else:
        instance_id = reco_id
        process_id = '0'

    return instance_id, process_id

class RecoProc(object):
    
    def __init__(self, id, inst):
        
        self.id = id
        self.inst = inst
        self.status_time = time.time()

        self.cameras = set()
        self.good_cameras = set()
        self.bad_cameras = set()
        self.not_connectedOnce = set()

        self.status = dict()

        self.status_cc = 0
        self.status_fps = 0.0
        self.period = 0.0
        pass

    def get_camera_status(self, camera_id):
        
        if camera_id not in self.cameras:
            return None
        
        stat = self.status.get(camera_id)

        if not self.status:
            return None

        return stat

    def set_status(self, status:list):
        
        # update 'connectedOnce'
        for c in status:
            #log.debug('proc camera: %s', c)
            cid = c['id']
            if c.get('capture',0) > 0 and cid in self.not_connectedOnce:
                try:
                    bvc_db.set_camera_property(cid, 'connectedOnce', True)
                    self.not_connectedOnce.discard(cid)
                except:
                    pass

        self.bad_cameras = set()
        self.good_cameras = set()

        tot_fps = 0.0

        new_status = dict()

        for c in status:
            cid = c.get('id')
            interval = c.get('interval',0)
            freq = 1000.0 / interval if interval > 0 else 0.0

            fps1 = c.get('capture',0) * freq
            fps2 = c.get('analyze',0) * freq

            if c.get('capture',0) > 0:
                self.good_cameras.add(cid)
                tot_fps += fps2
            else:
                self.bad_cameras.add(cid)

            stat = self.status.get(cid)
            if not stat:
                stat = c
            else:
                stat.update(c)

            tot2 = c.get('md_drop',0) + c.get('analyze',0)

            stat['fps1'] = fps1
            stat['fps2'] = fps2

            stat['md_per'] = c.get('md_drop',0) / tot2 if tot2 > 0 else 0.0

            new_status[cid] = stat

        self.status = new_status

        #log.debug('proc status: %s', self.status)

        self.status_cc = len(self.good_cameras)
        self.status_fps = tot_fps        

        now = time.time()
        self.period = now - self.status_time if self.status_time else 0.0
        self.status_time = now

    def append_camera(self, cid):
        
        self.cameras.add(cid)

        connectedOnce, _ = bvc_db.get_camera_property(cid, 'connectedOnce', False)

        if not connectedOnce:
            self.not_connectedOnce.add(cid)

        log.info("assing camera [%d] to %s", cid, self.id)
        pass

    def remove_camera(self, cid:int = None):
        
        if not cid:
            cid = random.choice(list(self.cameras))

        self.cameras.discard(cid)
            
        self.bad_cameras.discard(cid)
        self.good_cameras.discard(cid)
        self.not_connectedOnce.discard(cid)

        self.status.pop(cid, None)
        
        log.info("remove camera [%d] from %s", cid, self.id)

        return cid

    def get_cameras_min_quality(self, qmin:int):
        """
        qmin = 0: all cameras
        qmin > 0: connectedOnce cameras
        """

        if qmin > 0:
            return [c for c in self.cameras if c not in self.not_connectedOnce]

        return list(self.cameras)

    def purge(self, now = time.time()):

        if (now - self.status_time) <  purge_timeout:
            return set()

        log .warning("purge process: %s", self.id)

        if not self.cameras:
            return set()

        cs = self.cameras
        self.cameras = None

        return cs

    def is_purged(self):
        return self.cameras is None

class RecoInstance(object):
    
    def __init__(self, id):

        self.id = id

        self.status_cc = 0
        self.status_fps = 0.0

        self.fixfps = None
        self.fps_last = time.time()
        self.fix_start = None

        self.procs = {}

        pass

    def set_status(self, proc_id:str, status:list):
        
        new_proc = False

        proc = self.procs.get(proc_id)
        if proc is None:
            proc = RecoProc(self.id + ":" + proc_id, inst=self)
            self.procs[proc_id] = proc
            new_proc = True

        now = time.time()

        proc.set_status(status)

        status_cc = 0
        status_fps = 0.0

        for p in self.procs.values():
            status_cc += p.status_cc
            status_fps += p.status_fps
            
        self.status_cc = status_cc

        if self.fix_start:
            if (now - self.fix_start) >= fix_timeot and self.status_cc > 0 and self.status_fps > 0.0:
                self.fix_start = None

        if self.fixfps is None:
           self.fix_start = now 
           self.fixfps = 0.0

        d = now - self.fps_last
        self.fixfps = (self.fixfps * fix_window + status_fps * d) / (fix_window + d)
        self.fps_last = now

        self.status_fps = status_fps

        log.debug('instance set_status: %d %.2f', self.status_cc, self.status_fps)
        
        return new_proc

    def remove_proc(self, proc_id):
        
        proc = self.procs.get(proc_id)
        if proc is None:
            return None

        cs = proc.cameras

        self.procs.pop(proc_id)
        
        return cs

    def purge(self):

        now = time.time()        

        css = set()

        for k,p in self.procs.items():
            cs = p.purge(now)
            css |= cs

        self.procs = { k:p for k,p in self.procs.items() if not p.is_purged() }

        return css

    def is_purged(self):
        return not self.procs

    def is_fixed(self):
        return self.fixfps is not None and self.fix_start is None

    def _get_maxcam_proc(self):

        max_p = None
        for p in self.procs.values():
            if not max_p or len(p.cameras) > len(max_p.cameras):
                max_p = p
        
        return max_p

    def remove_camera(self, cid:int = None):
        
        if cid:
            
            for p in self.procs.values():
                if cid in p.cameras:
                    return p.remove_camera(cid)

            pass
        
        else:

            p = self._get_maxcam_proc()
            if p and p.cameras:
                return p.remove_camera()

        return None

    def append_camera(self, cid):
        
        if cid is None:
            return False

        ic = 0        
        min_p = None
        for p in self.procs.values():
            pc = len(p.cameras)
            ic += pc
            if not min_p or pc < len(min_p.cameras):
                min_p = p

        if min_p is None:
            return False

        if self.fixfps is None and ic == 0:
            self.stable_start = time.time()        

        min_p.append_camera(cid)

        return True

    def get_cameras_min_quality(self, qmin:int):
        
        xs = []
        for p in self.procs.values():
            xs.extend( p.get_cameras_min_quality(qmin) )

        return xs

    def get_total_count(self):
        
        cc = 0
        for p in self.procs.values():
            cc += len(p.cameras)

        return cc

    def get_active_count(self):
        
        cc = 0
        for p in self.procs.values():
            cc += len(p.good_cameras)

        return cc

    def get_availeable_for_moving_count(self):
        
        cc = 0
        for p in self.procs.values():
            n = len(p.cameras)
            if n > 0 :
                cc += n-1

        return cc

    def get_fpspc(self):
        
        cc = self.get_active_count()
        if cc == 0:
            cc += 1

        if self.fixfps is None:
            return not_fixed_fps / cc
        
        return self.fixfps / cc

    def redistribute(self):
        
        min_p = None
        max_p = None
        for p in self.procs.values():
            if not min_p or len(p.cameras) < len(min_p.cameras):
                min_p = p
            if not max_p or len(p.cameras) > len(max_p.cameras):
                max_p = p

        if min_p and max_p and len(min_p.cameras)+1 < len(max_p.cameras):
            c = max_p.remove_camera()
            min_p.append_camera(c)

class RecoDispatcher(object):

    def __init__(self):
        
        self.instances = {}

        self.free_cameras = set()

        self.lock = Lock()

        self.bStop = False

        self.worker = Thread(target=self._workerFunc)
        self.worker.start()        

        pass

    def stop(self, bWait = False):
        
        self.bStop = True

        if bWait:
            self.worker.join()
            self.worker = None

    def wait(self, interval):
        
        prev = time.time()

        while True:

            time.sleep(1.0)

            if self.bStop or (time.time()-prev) > interval:
                break

    def _workerFunc(self):
        
        # run
        log.info("RecoDispatcher worker start")

        while not self.bStop:

            with self.lock:

                try:

                    self._workerTick()

                except:
                    log.exception("[EX] _workerFunc")
                    pass

            self.wait(30.0)

        log.info("RecoDispatcher worker stop")
        pass

    def _workerTick(self):

        log.debug("worker Tick")

        self.purge()

        self.redistribute()

        pass        

    def _on_new_instance(self, inst_id):
        
        instance = RecoInstance(inst_id)
        self.instances[inst_id] = instance

        return instance

    def _on_del_instance(self):
        pass

    def _get_instance(self, inst_id):

        instance = self.instances.get(inst_id)

        if instance is None:
            instance = self._on_new_instance(inst_id)

        return instance

    def on_reco_end(self, reco_id):
        
        inst_id, proc_id = split_recoid(reco_id)

        log.info("reco proc ending: %s %s", inst_id, proc_id)

        with self.lock:
        
            instance = self._get_instance(inst_id)
            if instance:
                cs = instance.remove_proc(proc_id)
                if cs:
                    self.free_cameras.update(cs)

                    if len(instance.procs) == 0:
                        log.info("reco instance ending: %s", instance.id)
                        self.instances.pop(instance.id)
                        instance = None

                    self.redistribute()

        pass

    def set_reco_status(self, reco_id, status:list):
        """
        /api/reco_status handler
        """

        inst_id, proc_id = split_recoid(reco_id)

        #log.debug('set_reco_status: %s, %s', reco_id, status)

        # main
        with self.lock:
        
            instance = self._get_instance(inst_id)

            new_proc = instance.set_status(proc_id, status)

            if new_proc:
                self.redistribute()


    def on_reco_get_cameras(self, reco_id):
        """
        GET /api/active_cameras handler
        """

        with self.lock:

            inst_id, proc_id = split_recoid(reco_id)

            proc = self._get_proc(inst_id, proc_id)

            if not proc:
                return []

            cids = proc.cameras

            cameras = bvc_db.get_cameras_by_cids(list(cids))

            #logger.debug('on_reco_get_cameras: %s %s', str(cids), str(cameras))

            return cameras

    def on_cameras_update(self):
        """
        POST /api/user/cameras
        PUT /api/cameras/enabled
        DELETE /api/cameras/xx
        """

        try:

            with self.lock:
                cs = set(bvc_db.get_active_cameras())

                self._update_proc_cameras(cs)

                self.free_cameras = cs

                self.redistribute()

                pass

        except Exception as e:
            log.exception("[EX] on_cameras_update:")
            pass

    def get_camera_status(self, camera_id):
        """
        """
        with self.lock:
        
            for inst in self.instances.values():
                for proc in inst.procs.values():
                    
                    status = proc.get_camera_status(camera_id)
                    if status:
                        return status
                    
        return None
       
    def get_status(self):
        """
        """
        
        with self.lock:

            status = []

            now = time.time()

            for iid,inst in self.instances.items():
                procs = []
                for p in inst.procs.values():
                    
                    comments = ''

                    good_ss = [p.get_camera_status(cid) for cid in p.good_cameras]
                    fpss = [s.get('fps2',0.0) if s else 0.0 for s in good_ss]

                    procs.append({
                        'id': p.id, 
                        'cc': p.status_cc, 
                        'fps': p.status_fps, 
                        'prev': p.period,
                        'last': now - p.status_time,
                        'cids': list(p.cameras),
                        'fpss': fpss,
                        'good': list(p.good_cameras),
                        'bad': list(p.bad_cameras),
                        'comments': comments,
                    })

                procs = sorted(procs, key=lambda p: p['id'])

                comments = ''

                if not inst.is_fixed():
                    comments += ', not fixed'

                status.append({
                    'id': iid, 
                    'cc':inst.status_cc, 
                    'fps': inst.status_fps, 
                    'fixfps': inst.fixfps if inst.fixfps else 0.0, 
                    'fpspc':inst.get_fpspc(), 
                    'comments' : comments,
                    'procs':procs})


            status = { 
                'insts': sorted(status, key=lambda i: i['id']),
                'active_cameras': sorted(bvc_db.get_active_cameras()),
                'free_cameras': list(self.free_cameras)
            }

            return status
   
    def purge(self):
        
        css = set()
        for k,inst in self.instances.items():
            css |= inst.purge()

            if inst.is_purged():
                log.warning("purge instance: %s", inst.id)

        self.instances = { k:inst for k,inst in self.instances.items() if not inst.is_purged() }

        self.free_cameras |= css

        return bool(css)

    def _get_proc(self, instid, procid):
        
        inst = self.instances.get(instid)
        if not inst:
            return None

        proc = inst.procs.get(procid)
        
        return proc
            
    def _update_proc_cameras(self, active_cs: set):
        """
        removes not active cameras from procs
        removes proc's cameras from active_cs
        """
        
        for inst in self.instances.values():
            for p in inst.procs.values():
                if p.cameras is not None:
                    p.cameras &= active_cs
                    active_cs -= p.cameras

    def _get_empty_procs(self):
        
        ps = []
        
        for inst in self.instances.values():
            for p in inst.procs.values():

                if len(p.cameras)==0:
                    ps.append(p)

        return ps        

    def _get_empty_instances(self):
        
        ps = []
        
        for inst in self.instances.values():
            cc = 0
            for p in inst.procs.values():
                cc += len(p.cameras)

            if cc == 0:
                ps.append(inst)

        return ps        


    def _get_instance_min_loading(self):
        max_i = None
        for inst in self.instances.values():
            if not max_i or inst.get_fpspc() > max_i.get_fpspc():
                max_i = inst

        return max_i

    def ___get_instance_for_remove(self):

        min_i = None
        min_fps = 0

        for inst in self.instances.values():

            fps = inst.get_fpspc()
            cc = inst.get_cameras_count()

            if cc > 1 and (not min_i or fps < min_fps):
                min_i = inst
                min_fps = fps

        return min_i        

    def check_camera_moving(self):
        """
        returns two instances if camera's moving is preferable
        """

        min_i = None
        min_fps = 0
        min_fps2 = 0
        max_i = None
        max_fps = 0
        max_fps2 = 0

        for inst in self.instances.values():
            
            #if not inst.is_fixed():
            #    continue

            fps = inst.get_fpspc()

            ac = inst.get_availeable_for_moving_count()
            cc = inst.get_active_count()

            if cc > 1 and ac > 0 and (not min_i or fps < min_fps):
                min_i = inst
                min_fps = fps
                min_fps2 = fps * cc / (cc-1)

            if not max_i or fps > max_fps:
                max_i = inst
                max_fps = fps
                max_fps2 = fps * cc / (cc+1)

        if min_i and max_i and min_i != max_i and max_fps > 0 and max_fps2 > 0:

            #d1 = abs((max_fps-min_fps) / max_fps)
            #d2 = abs((max_fps2-min_fps2) / max_fps2)
            #if d2 < d1 * 1.5:

            d1 = min_fps
            d2 = max_fps2

            if d2 > d1:
                log.info('redistribute: %s->%s, %.2f->%.2f', min_i.id, max_i.id, d1, d2)                
                return min_i, max_i

        return None, None

    def _get_camera_for_free_proc(self, qmin):
        """
        searches instances for best camera to move it to free proc
        """
        
        min_i = None
        min_cs = None
        min_fps = 0

        for inst in self.instances.values():
            
            if not inst.is_fixed():
                continue

            fps = inst.get_fpspc()

            cs = inst.get_cameras_min_quality(qmin) 

            if len(cs) > 1 and (not min_i or fps < min_fps):
                min_i = inst
                min_cs = cs
                min_fps = fps

        if min_i is None:
            return None

        cid = random.choice(min_cs)

        return min_i.remove_camera(cid)

    def redistribute(self):

        # if there are more free processes than free_cameras

        free_procs = self._get_empty_procs()

        if len(free_procs) > 0:
            log.info("free procs count: %d", len(free_procs))

        while len(free_procs) > len(self.free_cameras):

            cid = self._get_camera_for_free_proc(1)
            if not cid:
                cid = self._get_camera_for_free_proc(0)
                if not cid:
                    break

            self.free_cameras.add(cid)

        # set cameras for free processes
        
        for c,p in list(zip(self.free_cameras, self._get_empty_procs())):
            if p.inst.append_camera(c):
                self.free_cameras.discard(c)
                

        # assign rest of free cameras

        while self.free_cameras:

            inst = self._get_instance_min_loading()
            if not inst:
                break

            inst.append_camera(self.free_cameras.pop())

        # move cameras from low fps to high
                
        min_i, max_i = self.check_camera_moving()

        if min_i and max_i:
            cid = min_i.remove_camera()
            max_i.append_camera(cid)

        # redistribute cameras inside of instance

        for inst in self.instances.values():
            inst.redistribute()

        pass
