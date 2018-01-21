import logging, logging.config
import bvc_config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(name)s: %(message)s',
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
            'filename' : 'logs/bvc.log',
            'formatter' : 'detail',
            'maxBytes': 10000000,
            'backupCount': 6,
        },

        'access': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename' : 'logs/bvc_access.log',
            'formatter' : 'detail',
            'maxBytes': 10000000,
            'backupCount': 6,
        },

        'errors': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename' : 'logs/bvc_errors.log',
            'formatter' : 'detail',
            'maxBytes': 10000000,
            'backupCount': 2,
        },
    },

    'loggers': {
        'werkzeug': {
            'level': 'INFO',
            'handlers': ['access'],
            'propagate': False
        },

        'gunicorn': {
            'level': 'INFO',
            'handlers': [],
            'propagate': True
        },

        'gunicorn.error': {
            'level': 'INFO',
            'handlers': [],
            'propagate': True
        },

        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['access'],
            'propagate': False
        },
     },

    'root': {
        'level': 'INFO',
        'handlers': ['console', 'infos', 'errors'],
    }
})
