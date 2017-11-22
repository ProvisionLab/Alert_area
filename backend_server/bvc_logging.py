import logging, logging.config
import bvc_config

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
        'infos': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename' : 'bvc.log',
            'formatter' : 'detail',
            'maxBytes': 10000000,
            'backupCount': 2,
        },
        'errors': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename' : 'bvc_errors.log',
            'formatter' : 'detail',
            'maxBytes': 10000000,
            'backupCount': 6,
        },
    },

    'loggers': {
        'werkzeug': {
            'level': 'INFO',
            'handlers': [],
            'propagate': True
        }
    },

    'root': {
        'level': 'INFO',
        'handlers': ['console', 'infos', 'errors'],
    }
})
