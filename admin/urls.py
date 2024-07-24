from flask import Blueprint

admin = Blueprint('admin', __name__)
@admin.route('/<page>')
def show(page):
    pass