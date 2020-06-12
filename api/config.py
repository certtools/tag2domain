
import os

"""
Config file
"""

config = dict()
config.update(dict(
    version=0.2,
    debug=True,
    loglevel="DEBUG",                   # valid values: DEBUG, INFO, WARN, ERROR (same as default python logging)
    admin_pwd=os.getenv('ADMIN_PWD'),   # a master fallback pwd for the admin user
    DATABASE=os.getenv('DB'),
    USERNAME=os.getenv('DBUSER'),
    PASSWORD=os.getenv('DBPASS'),
    DBHOST=os.getenv('DBHOST'),
    DBPORT=5432,
    SECRET_KEY="oothiedeevoophu6Zohm9au5ceem2dadeicood8saiy6Aetiekaizaht2ogheije",  # for web stuff
    baseurl='http://localhost:8000',
    MAIL_FROM="kaplan@nic.at",
    default_limit=1000,
    default_offset=0,
))


if __name__ == "__main__":
    print(config)
