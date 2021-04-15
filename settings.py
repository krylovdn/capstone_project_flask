from flask import Flask
from configparser import ConfigParser

app = Flask(__name__)

parser = ConfigParser()
parser.read('./config.ini')

app.config['SQLALCHEMY_DATABASE_URI'] = parser.get('db', 'db_uri')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = parser.getboolean('db', 'track_modifications')

app.config['LOG_FILE_NAME'] = parser.get('settings', 'log_path')

app.config['SECRET_KEY'] = 'super_secret_key'
