import time
import logging
import bvc_db
from threading import Lock
from threading import Thread

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
        self.status_time = None

        self.cameras = set()
        pass

    def set_status(self, cc, fps):
        
        self.status_cc = cc
        self.status_fps = fps        

        now = time.time()
        self.period = now - self.status_time if self.status_time else 0.0
        self.status_time = now

        logging.info('proc set_status: %d %.2f', self.status_cc, self.status_fps)

    def add_camera(self, cid):
        
        self.cameras.add(cid)
        pass

    def purge(self, now = time.time()):

        if (now - self.status_time) <  purge_timeout:
            return set()

        logging.warning("purge process: %s", self.id)

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
        self.fixfps = None
        self.fps_last = time.time()
        self.fix_start = None

        self.procs = {}

        pass

    def set_status(self, proc_id, cc, fps):
        
        new_proc = False

        proc = self.procs.get(proc_id)
        if proc is None:
            proc = RecoProc(self.id + ":" + proc_id, inst=self)
            self.procs[proc_id] = proc
            new_proc = True

        now = time.time()

        proc.set_status(cc, fps)

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

        logging.info('instance set_status: %d %.2f', self.status_cc, self.status_fps)
        return new_proc

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

    def remove_camera(self):

        p = self._get_maxcam_proc()
        if p and p.cameras:
            return p.cameras.pop()

        return None

    def add_camera(self, cid):
        
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

        min_p.cameras.add(cid)

        return True

    def get_cameras_count(self):
        
        cc = 0
        for p in self.procs.values():
            cc += len(p.cameras)

        return cc

    def get_fpspc(self):
        
        cc = self.get_cameras_count()
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
            c = max_p.cameras.pop()
            min_p.cameras.add(c)

class RecoDispatcher(object):

    def __init__(self):
        
        bvc_db.mutex_init('procs')
        bvc_db.mutex_init('disp')
        
        self.instances = {}

        self.free_cameras = {}

        self.lock = Lock()

        self.worker = Thread(target=self._workerFunc)
        self.worker.start()        
        pass

    def _workerFunc(self):
    
        with bvc_db.DatabaseLock("disp"):
    
            while True:
    
                bvc_db.mutex_confirm("disp")                
    
                self._workerTick()
    
                time.sleep(30.0)

        pass

    def _workerTick(self):

        #logging.debug("worker Tick")

        bvc_db.reco_purge_procs(300.0)

        # 2do:
        # purge procs
        # dispatch cameras

        pass

    def _on_new_instance(self, inst_id):
        
        instance = RecoInstance(inst_id)
        self.instances[inst_id] = instance

        return instance

    def _on_del_instance(self):
        pass

    def set_reco_state(self, reco_id, fps, cameras):
        """
        /api/rs handler
        """

        inst_id, proc_id = split_recoid(reco_id)

        cameras_count = len(cameras)

        with bvc_db.DatabaseLock('procs'):

            bvc_db.reco_update_proc(inst_id, proc_id, cameras_count, fps)

        with self.lock:
        
            inst_id, proc_id = split_recoid(reco_id)

            instance = self.instances.get(inst_id)

            if instance is None:
                instance = self._on_new_instance(inst_id)

            new_proc = instance.set_status(proc_id, cameras_count, fps)

            new_free = self.purge()

            if new_proc or new_free:
                pass

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

            #logging.info('on_reco_get_cameras: %s %s', str(cids), str(cameras))

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
            logging.exception(e)
            pass
       
    def get_status2(self):
        """
        """

        status = []
        now = time.time()

        with bvc_db.RecoLock():

            status = bvc_db.reco_get_status()

            pass

        return {}
       
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

                    procs.append({
                        'id': p.id, 
                        'cc': p.status_cc, 
                        'fps': p.status_fps, 
                        'prev': p.period,
                        'last': now - p.status_time,
                        'cids': p.cameras,
                        'comments': comments
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
                'free_cameras': self.free_cameras
            }

            return status
   
    def purge(self):
        
        css = set()
        for k,inst in self.instances.items():
            css |= inst.purge()

            if inst.is_purged():
                logging.warning("purge instance: %s", inst.id)

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


    def get_instance_for_add(self):
        max_i = None
        for inst in self.instances.values():
            if not max_i or inst.get_fpspc() > max_i.get_fpspc():
                max_i = inst

        return max_i

    def get_instance_for_remove(self):

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

            fps = inst.get_fpspc()
            cc = inst.get_cameras_count()

            if cc > 1 and (not min_i or fps < min_fps):
                min_i = inst
                min_fps = fps
                min_fps2 = fps * cc / (cc-1)

            if not max_i or fps > max_fps:
                max_i = inst
                max_fps = fps
                max_fps2 = fps * cc / (cc+1)

        if min_i and max_i and max_fps > 0 and max_fps2 > 0:

            d1 = abs((max_fps-min_fps) / max_fps)
            d2 = abs((max_fps2-min_fps2) / max_fps2)

            if d2 < d1 * 1.5:
                logging.info('redistribute: %s->%s, %.2f->%.2f', min_i.id, max_i.id, d1, d2)                
                return min_i, max_i

        return None, None
        

    def redistribute(self):

        # if there are more free processes than free_cameras

        free_procs = self._get_empty_procs()

        while len(free_procs) > len(self.free_cameras):
            inst = self.get_instance_for_remove()
            if not inst:
                break

            cid = inst.remove_camera()
            if not cid:
                break

            self.free_cameras.add(cid)

        # set cameras for free processes
        
        for c,p in list(zip(self.free_cameras, self._get_empty_procs())):
            if p.inst.add_camera(c):
                self.free_cameras.discard(c)


        # assign rest of free cameras

        while self.free_cameras:

            inst = self.get_instance_for_add()

            if not inst:
                break

            inst.add_camera(self.free_cameras.pop())

        # move cameras from low fps to high
                
        min_i, max_i = self.check_camera_moving()

        if min_i and max_i:
            cid = min_i.remove_camera()
            max_i.add_camera(cid)

        # redistribute cameras inside of instance

        for inst in self.instances.values():
            inst.redistribute()

        pass
