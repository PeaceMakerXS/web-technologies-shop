import os
from dotenv import load_dotenv
load_dotenv()

class Config:
	MEDIA_FOLDER = 'media'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
