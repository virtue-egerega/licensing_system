from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += []

LOGGING["root"]["level"] = "DEBUG"
LOGGING["loggers"]["core"]["level"] = "DEBUG"
LOGGING["loggers"]["api"]["level"] = "DEBUG"
