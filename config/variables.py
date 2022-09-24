import os
from dotenv import load_dotenv


def set_up():
    """Sets up configuration for the app"""

    load_dotenv()

    config = {
        "google": {
            "id": os.getenv("GOOGLE_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET")
        },
        "database": {
            "password": os.getenv("DATABASE_PASSWORD"),
            "user": os.getenv("DATABASE_USER"),
            "name": os.getenv("DATABASE_NAME"),
            "port": os.getenv("DATABASE_PORT", 5432),
        },
        "email": {
            "user": os.getenv("EMAIL_USER"),
            "password": os.getenv("EMAIL_PASSWORD"),
            "host": os.getenv("EMAIL_HOST"),
            "port": os.getenv("EMAIL_PORT")
        },
        "secret": os.getenv("APP_SECRET_KEY"),
        "domain": os.getenv("DOMAIN"),
        "protocol": os.getenv("PROTOCOL", "https://"),
        "port": os.getenv("PORT", 443),
        "debug": os.getenv("DEBUG", False),
        "name": os.getenv("APP_NAME", "App")
    }

    return config
