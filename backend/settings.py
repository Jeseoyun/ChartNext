import sys
import logging

# 파일 시스템 로거 비활성화
logging.getLogger('django.utils.autoreload').setLevel(logging.ERROR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'CRITICAL',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'django.template': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'django.utils.autoreload': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        '': {
            'handlers': ['null'],
            'level': 'CRITICAL',
            'propagate': False,
        }
    }
}

# 추가 설정
DEBUG = False
SILENCED_SYSTEM_CHECKS = ['*']

# 자동 리로드 비활성화
USE_RELOADER = False

# 템플릿 로딩 최적화
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]