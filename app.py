from flask import Flask
from accounts.urls import account
from admin.urls import admin
from flask import Flask,g,current_app
from flask_pymongo import PyMongo
from pymongo import MongoClient

from flask_cors import CORS

from dotenv import load_dotenv





def get_db():
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client[current_app.config['DATABASE_NAME']]
    return g.db

def create_app(config_class='config.DevelopmentConfig'):
    load_dotenv('.env')
    app = Flask(__name__)
    CORS(app, supports_credentials=True) 
    
    
    
    app.config.from_object(config_class)

    
    
    with app.app_context():
        

        app.register_blueprint(account, url_prefix='/account')
        app.register_blueprint(admin, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
