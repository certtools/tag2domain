INSERT INTO tags (tag_id, tag_name, tag_description, taxonomy_id, extras) VALUES (2000561, 'cat_1::test_tag_1_tax_4', 'test tag 1 for tax 4 (cat 1)', 4, '{}');
INSERT INTO tags (tag_id, tag_name, tag_description, taxonomy_id, extras) VALUES (2000562, 'cat_1::test_tag_2_tax_4', 'test tag 2 for tax 4 (cat 1)', 4, '{}');
INSERT INTO tags (tag_id, tag_name, tag_description, taxonomy_id, extras) VALUES (2000563, 'cat_2::test_tag_3_tax_4', 'test tag 3 for tax 4 (cat 2)', 4, '{}');
INSERT INTO tags (tag_id, tag_name, tag_description, taxonomy_id, extras) VALUES (2000564, 'test_tag_4_tax_4', 'test tag 4 for tax 4 (no cat)', 4, '{}');

INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 2000561, '20200317', null, 1, null, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 2000562, '20200317', null, 1, null, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');

INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 2000563, '20200317', null, 1, null, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');

INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (2, 2000563, '20200317', null, 1, null, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');

INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 2000564, '20200317', null, 1, null, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');