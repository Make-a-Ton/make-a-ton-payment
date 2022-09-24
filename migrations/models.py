from config.db import Base
import auth.models
import home.models


def get_metadata():
    return Base.metadata
