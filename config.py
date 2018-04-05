import os
class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOEN=True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASKY_MAIL_SENDER='guojixue<2403023881@qq.com>'
    FLASKY_ADMIN='m15574816184@163.com'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG=True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = '2403023881@qq.com'
    MAIL_PASSWORD = 'ezemvmgvugjmebic'
    SQLALCHEMY_DATABASE_URI="mysql://root:123456@localhost/dev_flask"

class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI="mysql://root:123456@localhost/test_flask"

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI="mysql://root:123456@localhost/product_flask"

config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}