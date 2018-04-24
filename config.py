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
    Role_Admin="6d0daadf499f48f9a1be1561e85e9ab7"
    Role_User="98f6a13389e54c20b8711104efa29342"
    Domein_id="80625893030640d4817ef31e5319d3e9s"
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