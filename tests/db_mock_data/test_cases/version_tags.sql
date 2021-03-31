INSERT INTO taxonomy_tag_val (id, value, tag_id) VALUES (100001, '1.0.2', 2);
INSERT INTO taxonomy_tag_val (id, value, tag_id) VALUES (100002, '2.1.0', 2);

INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 2, '20200317', null, 1, 100001, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (2, 2, '20200317', null, 1, 100002, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (3, 2, '20200317', '20200820', 1, 100002, to_timestamp('2020-08-20 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'),  to_timestamp('2020-08-20 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), 'test_producer1');