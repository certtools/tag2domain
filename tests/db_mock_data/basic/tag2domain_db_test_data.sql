CREATE SCHEMA IF NOT EXISTS tag2domain;
SET search_path TO tag2domain;

INSERT INTO public.registrars (registrar_name) VALUES ('registrar_1');
INSERT INTO public.registrars (registrar_name) VALUES ('registrar_2');
INSERT INTO public.registrars (registrar_name) VALUES ('registrar_3');

INSERT INTO public.domains (domain_name) VALUES ('test1.at');
INSERT INTO public.domains (domain_name) VALUES ('test2.at');
INSERT INTO public.domains (domain_name) VALUES ('test3.at');
INSERT INTO public.domains (domain_name) VALUES ('test4.at');
INSERT INTO public.domains (domain_name) VALUES ('test5.at');

INSERT INTO public.delegations (domain_id, registrar_id, create_ts, purge_ts) VALUES (1, 1, '2020-01-17 12:53:21', NULL);
INSERT INTO public.delegations (domain_id, registrar_id, create_ts, purge_ts) VALUES (2, 1, '2020-02-17 12:53:21', '2020-06-30 04:00:00');
INSERT INTO public.delegations (domain_id, registrar_id, create_ts, purge_ts) VALUES (3, 2, '2020-05-01 14:00:00', NULL);
INSERT INTO public.delegations (domain_id, registrar_id, create_ts, purge_ts) VALUES (4, 2, '2020-01-17 12:53:21', NULL);
INSERT INTO public.delegations (domain_id, registrar_id, create_ts, purge_ts) VALUES (5, 3, '2020-08-20 23:50:00', NULL);

INSERT INTO taxonomy (name, description, is_actionable, is_automatically_classifiable, is_stable, for_numbers, for_domains, url, allows_auto_tags, allows_auto_values) VALUES ('tax_test1', 'test taxonomie 1', 1, true, false, true, true, 'test.at/test_taxonomie_1', false, false);
INSERT INTO taxonomy (name, description, is_actionable, is_automatically_classifiable, is_stable, for_numbers, for_domains, url, allows_auto_tags, allows_auto_values) VALUES ('tax_test2', 'test taxonomie 2', 1, true, false, true, true, 'test.at/test_taxonomie_2', true, false);
INSERT INTO taxonomy (name, description, is_actionable, is_automatically_classifiable, is_stable, for_numbers, for_domains, url, allows_auto_tags, allows_auto_values) VALUES ('tax_test3', 'test taxonomie 3', 0.5, true, false, true, true, 'test.at/test_taxonomie_3', false, true);
INSERT INTO taxonomy (name, description, is_actionable, is_automatically_classifiable, is_stable, for_numbers, for_domains, url, allows_auto_tags, allows_auto_values) VALUES ('tax_test4', 'test taxonomie 4', NULL, true, false, true, true, 'test.at/test_taxonomie_4', true, true);

INSERT INTO tags (tag_name, tag_description, taxonomy_id, extras) VALUES ('test_tag_1_tax_1', 'test tag 1 for tax 1', 1, '{}');
INSERT INTO tags (tag_name, tag_description, taxonomy_id, extras) VALUES ('test_tag_2_tax_1', 'test tag 2 for tax 1', 1, '{}');
INSERT INTO tags (tag_name, tag_description, taxonomy_id, extras) VALUES ('test_tag_3_tax_1', 'test tag 3 for tax 1', 1, '{}');
INSERT INTO tags (tag_name, tag_description, taxonomy_id, extras) VALUES ('test_tag_1_tax_3', 'test tag 1 for tax 3', 3, '{}');

INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('value_1_tag_1', 1);
INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('value_2_tag_1', 1);
INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('value_1_tag_4', 4);

INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 1, '20200317', null, 1, null, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (2, 1, '20200317', null, 1, 1, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, null);
INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 2, '20200425', null, 1, null, to_timestamp('2020-06-30 20:51:36', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 3, '20200425', '20200710', 1, null, to_timestamp('2020-07-10 14:20:00', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-07-10 14:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'test_producer3');
INSERT INTO domain_tags (domain_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 4, '20200425', null, 3, null, to_timestamp('2020-06-30 20:51:36', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer3');

INSERT INTO delegation_tags (delegation_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 1, '20200317', null, 1, null, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO delegation_tags (delegation_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (2, 1, '20200317', null, 1, 1, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, null);
INSERT INTO delegation_tags (delegation_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 2, '20200425', null, 1, null, to_timestamp('2020-06-30 20:51:36', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO delegation_tags (delegation_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 3, '20200425', '20200710', 1, null, to_timestamp('2020-07-10 14:20:00', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-07-10 14:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'test_producer3');
INSERT INTO delegation_tags (delegation_id, tag_id, start_date, end_date, taxonomy_id, value_id, measured_at, start_ts, end_ts, producer)
                 VALUES (1, 4, '20200425', null, 3, null, to_timestamp('2020-06-30 20:51:36', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer3');

INSERT INTO intersections (intxn_id, pickerl_id, datum_start, datum_ende, taxonomie_id, beschriftung_id, gemessen_um, zeitstempel_start, zeitstempel_ende, erzeuger)
                 VALUES (1, 1, '20200317', null, 1, null, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO intersections (intxn_id, pickerl_id, datum_start, datum_ende, taxonomie_id, beschriftung_id, gemessen_um, zeitstempel_start, zeitstempel_ende, erzeuger)
                 VALUES (2, 1, '20200317', null, 1, 1, to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-03-17 12:53:21', 'YYYY-MM-DD HH24:MI:SS'), null, null);
INSERT INTO intersections (intxn_id, pickerl_id, datum_start, datum_ende, taxonomie_id, beschriftung_id, gemessen_um, zeitstempel_start, zeitstempel_ende, erzeuger)
                 VALUES (1, 2, '20200425', null, 1, null, to_timestamp('2020-06-30 20:51:36', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer1');
INSERT INTO intersections (intxn_id, pickerl_id, datum_start, datum_ende, taxonomie_id, beschriftung_id, gemessen_um, zeitstempel_start, zeitstempel_ende, erzeuger)
                 VALUES (1, 3, '20200425', '20200710', 1, null, to_timestamp('2020-07-10 14:20:00', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-07-10 14:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'test_producer3');
INSERT INTO intersections (intxn_id, pickerl_id, datum_start, datum_ende, taxonomie_id, beschriftung_id, gemessen_um, zeitstempel_start, zeitstempel_ende, erzeuger)
                 VALUES (1, 4, '20200425', null, 3, null, to_timestamp('2020-06-30 20:51:36', 'YYYY-MM-DD HH24:MI:SS'), to_timestamp('2020-04-25 18:21:00', 'YYYY-MM-DD HH24:MI:SS'), null, 'test_producer3');
