import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

# get variables to create postgres url
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PASSWORD')
PG_URL = os.getenv('POSTGRES_URL')
PG_DB = os.getenv('POSTGRES_DB')
PG_PORT = os.getenv('POSTGRES_PORT')

PG_URI = f"postgresql://{PG_USER}:{PG_PW}@{PG_URL}:{PG_PORT}/{PG_DB}"
print("HELLO THERE")
