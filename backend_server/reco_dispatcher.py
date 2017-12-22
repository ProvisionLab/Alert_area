import logging

class RecoDispatcher(object):

    def __init__(self):
        pass

    def on_reco_request(self, reco_id):
        
        i = reco_id.rfind(':')
        if i >= 0:
            instance_id = reco_id[:i]
            process_id = reco_id[i+1:]
        else:
            instance_id = reco_id
            process_id = '0'

        logging.info('on_reco_instance_request, \'%s\', \'%s\'', instance_id, process_id)
        
        pass
       