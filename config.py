import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(64)
    SSL_DISABLE = False
    
    # alchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    
    # flask mail
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    
    # celery
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    FAUCET_MAIL_SUBJECT_PREFIX = "[faucet]"
    FAUCET_MAIL_SENDER = "Faucet Admin <valvefaucet@protonmail.com>"
    FAUCET_ADMIN = os.environ.get("FAUCET_ADMIN")

    # bitcoinlib
    BITCOINLIB_DB_USER = os.environ.get("BITCOINLIB_DB_USER") or "bitcoinlib"
    BITCOINLIB_DB_PASSWORD = os.environ.get("BITCOINLIB_DB_PASSWORD") or "yufakay3"
    BITCOINLIB_RPC_USER = os.environ.get("RPC_USERNAME") or "bitcoinlib"
    BITCOINLIB_RPC_PASSWORD = os.environ.get("RPC_PASSWORD") or "yufakay3"
    BITCOINLIB_RPC_AUTH = BITCOINLIB_RPC_USER + ":" + BITCOINLIB_RPC_PASSWORD
    BITCOINLIB_DB_URI = "mysql://" + BITCOINLIB_DB_USER + ":" + BITCOINLIB_DB_PASSWORD + \
        "@localhost:3306/bitcoinlib"
    BITCOINLIB_RPC_SERVER = "http://" + BITCOINLIB_RPC_AUTH + "@127.0.0.1:18332"

    # json
    JSONIFY_PRETTYPRINT_REGULAR = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data-test.sqlite")
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data.sqlite")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, "MAIL_USERNAME", None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, "MAIL_USE_TLS", None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FAUCET_MAIL_SENDER,
            toaddrs=[cls.FAUCET_ADMIN],
            subject=cls.FAUCET_MAIL_SUBJECT_PREFIX + " Application Error",
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}