import os 
class Config:
    MONGO_URI = os.environ.get('MONGO_URI')
    DATABASE_NAME=os.environ.get('DATABASE_NAME')
    # PATH=os.path.join(os.getcwd(),os.environ.get('FILE_NAME'))
class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True