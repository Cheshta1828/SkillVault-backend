from flask import Blueprint
account = Blueprint('account', __name__)
from . import views
from .views import *

account.add_url_rule('/register', 'register', views.register, methods=['POST'])

account.add_url_rule('/login', 'login', views.login, methods=['POST'])
account.add_url_rule('/protected', 'protected', views.protected, methods=['GET'])
account.add_url_rule('/logout', 'logout', views.logout, methods=['POST'])
account.add_url_rule('/resend_email_verification', 'resend_email_verification', views.resend_email_verification, methods=['POST'])