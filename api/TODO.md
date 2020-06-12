# DB

- [ ] automate the tagging and make sure the views (v_taxonomies_domains, ...) always return the latest view (or allow for timed view slices)
- [ ] v_taxonomies_domains : name -> taxonomy_name, missing: taxonomy_id in the view
- [ ] create view in db/* files

# General TODOs

- [ ] Documentation on github
- [ ] Separate db / config for nic.at repo and github repo
- [ ] fix API endpoint URLs everywhere, are they pretty?
- [ ] let the python sample code be generated (see https://openapi-generator.tech/#try)
- [ ] refactor: all the limit= and offset GET params should be a decorator
- [ ] add timing and other meta-infos to the responses (see middleware)
- [ ] blueprints/ refactor files

# Testing
- [ ] at least one unit test for every API endpoint and every function
- [ ] expose unit tests in API under meta/tests/...
- [ ] expose liveliness check under meta/ping-test

# Specifics

## get_tags_by_domain

- [ ] variant: by suffix
- [ ] variant: by substring (infix)
- [ ] assign a tag to every domain? like at least "normal domain"?
