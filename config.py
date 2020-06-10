import os


class Config:
    SECRT_KEY = 'mrsoft'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        """初始化配置文件"""
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:root@127.0.0.1:3306/shop'
    DEBUG = True


config = {
    'default': DevelopmentConfig
}
