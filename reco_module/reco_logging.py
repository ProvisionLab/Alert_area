import os
import logging, logging.config
import reco_config

reco_id = int(os.environ.get('RECO_PROC_ID', '1'))
reco_count = int(os.environ.get('RECO_TOTAL_PROCS', '1'))

sufix = '_'+str(reco_id) if reco_count > 1 else ''


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
            'level': 'DEBUG' if reco_config.DEBUG else 'INFO',
            'class':'logging.StreamHandler',
            'formatter' : 'simple',
        },
        'infos': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename' : 'logs/reco' + sufix + '.log',
            'formatter' : 'detail',
            'maxBytes': 10000000,
            'backupCount': 2,
        },
        'errors': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename' : 'logs/reco_errors' + sufix + '.log',
            'formatter' : 'detail',
            'maxBytes': 10000000,
            'backupCount': 6,
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
        'level': 'INFO',
        'handlers': ['console', 'infos', 'errors'],
    }
})
