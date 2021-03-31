SET search_path TO :t2d_schema;

--
-- taxonomies
--
INSERT INTO taxonomy
    (name, description, is_actionable, is_automatically_classifiable, is_stable, for_numbers, for_domains, url, allows_auto_tags, allows_auto_values)
    VALUES
    ('colors', 'Test taxonomy 1 - colors', 1, true, false, true, true, 'https://test1.com', false, false)
;

INSERT INTO taxonomy
    (name, description, is_actionable, is_automatically_classifiable, is_stable, for_numbers, for_domains, url, allows_auto_tags, allows_auto_values)
    VALUES
    ('flavors', 'Test taxonomy 2 - flavors', 0, true, false, true, true, 'https://test2.com', true, true)
;

--
-- tags and values
--
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('rgb::red','Red', 1); -- 1
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('rgb::green','Green', 1); -- 2
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('rgb::blue','Blue', 1); -- 3
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('cmyk::cyan','Cyan', 1); -- 4
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('cmyk::magenta','Magenta', 1); -- 5
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('cmyk::yellow','Yellow', 1); -- 6
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('cmyk::black','Black', 1); -- 7

INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('sweet','Sweet', 2); -- 8
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('salty','Salty', 2); -- 9
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('sour','Sour', 2); -- 10
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('bitter','Bitter', 2); -- 11
INSERT INTO tags (tag_name, tag_description, taxonomy_id) VALUES ('umami','Umami', 2); -- 12

INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('very', 8); -- 1
INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('a little', 8); -- 2

INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('lightly', 9); -- 3
INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('strongly', 9); -- 4

INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('lemony', 10); -- 5
INSERT INTO taxonomy_tag_val (value, tag_id) VALUES ('a touch', 10); -- 6

--
-- intersections
--

INSERT INTO intersections (entity_id, tag_id, start_date, end_date, taxonomy_id, value_id, start_ts, measured_at, end_ts, producer)
    VALUES (1, 1, 20201020, NULL    , 1, NULL,'2020-10-20T09:00:00', '2020-11-23T12:00:00', NULL               , 'init1');

INSERT INTO intersections (entity_id, tag_id, start_date, end_date, taxonomy_id, value_id, start_ts, measured_at, end_ts, producer)
    VALUES (1, 4, 20201020, 20201020, 1, NULL,'2020-10-10T23:51:00', '2020-10-19T12:00:00', '2020-10-20T09:00:00', 'init1');

INSERT INTO intersections (entity_id, tag_id, start_date, end_date, taxonomy_id, value_id, start_ts, measured_at, end_ts, producer)
    VALUES (1, 9, 20201020, NULL    , 1,    4,'2020-10-12T23:51:00',  '2020-10-28T06:40:00', NULL                 , 'init2');

INSERT INTO intersections (entity_id, tag_id, start_date, end_date, taxonomy_id, value_id, start_ts, measured_at, end_ts, producer)
    VALUES (1, 9, 20201020, 20201028, 1,    3,'2020-10-14T23:51:00',  '2020-10-28T06:40:00', '2020-10-28T06:40:00', 'init2');