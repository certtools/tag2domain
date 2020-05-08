# tag2domain

The tag2domain DB parts which can be integrated into the DWH. 
Note that this repo is the **internal** nic.at version. The public version of tag2domain does not contain all the values which we might have in our DB.

# Installation

This repository assumes that the ``dwh`` DB structure already exists. The tag2domain tables integrate into the ``dwh`` database.
Hence, in order to get the tag2domain tables installed, please execute the following SQL scripts:

```bash
psql -h $server -U $user $db < db/taxonomy.sql
psql -h $server -U $user $db < db/tags.sql
psql -h $server -U $user $db < db/taxonomy_tag_val.sql.sql
psql -h $server -U $user $db < db/domain_tags.sql

```


Note that the domain_tags intersection table might be adapted for your purposes. It is only given as an example.


# DB structure

![EER Diagram](schema.png)

# Adding data

# Server.py

# The global awesome taxonomy list project

There is a [global taxonomy list](https://github.com/aaronkaplan/awesome-taxonomyzoo-list) on github, which serves as a place for anyone to propose taxonomies and document them.
This list should be  constantly growing by community contributions (should this project kick off). The important aspect for us  is that every taxonomy is described as machine readable **machine-tag** format.
Hence, we can include other taxonomies into our DB rather easily.


