import time
import logging
import bvc_db
from threading import Lock
from threading import Thread

purge_timeout = 300  # seconds

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

class RecoDispatcher2(object):

    def __init__(self):
        
        bvc_db.mutex_init('procs')
        bvc_db.mutex_init('disp')

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

        pass

    def _workerFunc(self):
    
        with bvc_db.DatabaseLock("disp"):
            
            # load state from database
            # 2do:

            # run
            while not self.bStop:
    
                bvc_db.mutex_confirm("disp")                
    
                self._workerTick()
    
                self.wait(30.0)

        pass

    def _workerTick(self):

        #logging.debug("worker Tick")

        self.purge()

        # 2do:
        # purge procs
        # dispatch cameras

        pass

    def set_reco_status(self, reco_id, fps, cameras):
        """
        /api/reco_status handler
        """

        inst_id, proc_id = split_recoid(reco_id)

        with bvc_db.DatabaseLock('procs'):

            bvc_db.reco_update_proc(inst_id, proc_id, cameras)

    def get_status(self):
        """
        """

        status = bvc_db.reco_get_status()

        return status
       
    def purge(self):
        
        bvc_db.reco_purge_procs(300.0)        
