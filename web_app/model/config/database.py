import os


host = os.environ["DATABASE_HOST"]
name = os.environ["DATABASE_NAME"]
name = os.environ["DATABASE_USER"]
password = os.environ["DATABASE_PASSWORD"]


url_db = {
    "sqlalchemy.url": f'postgresql+psycopg://{os.environ["DATABASE_USER"]}:{os.environ["DATABASE_PASSWORD"]}@{os.environ["DATABASE_HOST"]}/{os.environ["DATABASE_NAME"]}'
}
async_url_db = url_db["sqlalchemy.url"]
