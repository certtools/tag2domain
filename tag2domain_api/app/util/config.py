import os
from dotenv import load_dotenv, find_dotenv


"""
Config file
"""

load_dotenv(find_dotenv(), verbose=True)

description = """
## A RESTful API for querying the tag2domain DB.

You can query the database of mappings of domains to tags.
See [the github repository](https://github.com/certtools/tag2domain) for
further information.

Authors: Aaron Kaplan <[kaplan@nic.at](kaplan@nic.at)> and
[Clemens Moritz](https://github.com/cleboo)

**Copyright** 2021 (C) nic.at GmbH, all rights reserved.

**License**: GNU Affero General Public License v3.0. See the LICENSE file for
details.

"""

config = dict()
config.update(dict(
    version='0.8.4',
    # valid values: DEBUG, INFO, WARN, ERROR (same as default python logging)
    loglevel=os.getenv('LOG_LEVEL', 'INFO'),
    baseurl='http://localhost:' + os.getenv('PORT', '80'),
    default_limit=1000,
    default_offset=0,
    # DB stuff
    DBHOST=os.getenv('DBHOST', 'localhost'),
    DBPORT=os.getenv('DBPORT', '5432'),
    DATABASE=os.getenv('DB'),
    DBUSER=os.getenv('DBUSER'),
    DBPASSWORD=os.getenv('DBPASSWORD'),
    DBSSLMODE=os.getenv('DBSSLMODE', 'require'),
    DBTAG2DOMAIN_SCHEMA=os.getenv('DBTAG2DOMAIN_SCHEMA', 'tag2domain'),
    ENABLE_MSM2TAG=(os.getenv('ENABLE_MSM2TAG', False) == 'True'),
    MSM2TAG_MAX_MEASUREMENT_AGE=os.getenv('MSM2TAG_MAX_MEASUREMENT_AGE', None),
    MSM2TAG_DB_CONFIG=os.getenv('MSM2TAG_DB_CONFIG', None)
))

if __name__ == "__main__":
    print(config)
