import logging

from tag2domain_api.app.util.config import config


def setup():
    logging.basicConfig(
        level=config['loglevel'],
        format='[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z'
    )
