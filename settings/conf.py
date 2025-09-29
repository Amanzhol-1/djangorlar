from decouple import config


# ----------------------------------------------
# Env id
#
ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)
ENV_ID = config("DJANGORLAR_ENV_ID", default="local", cast=str)
SECRET_KEY = config('django-secret-key-example', default='secret')