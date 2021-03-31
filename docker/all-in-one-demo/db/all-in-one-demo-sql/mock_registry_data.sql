INSERT INTO public.domains (domain_name) VALUES ('domain_test1.at');
INSERT INTO public.domains (domain_name) VALUES ('domain_test2.at');
INSERT INTO public.domains (domain_name) VALUES ('domain_test3.at');
INSERT INTO public.domains (domain_name) VALUES ('domain_test4.at');
INSERT INTO public.domains (domain_name) VALUES ('domain_test5.at');

INSERT INTO public.registrars (registrar_name) VALUES ('registrar_1');
INSERT INTO public.registrars (registrar_name) VALUES ('registrar_2');
INSERT INTO public.registrars (registrar_name) VALUES ('registrar_3');

INSERT INTO public.delegations (registrar_id, domain_id, start_ts, end_ts) VALUES (1, 1, '2020-10-10T12:00:00', NULL);
INSERT INTO public.delegations (registrar_id, domain_id, start_ts, end_ts) VALUES (1, 1, '2016-03-01T08:31:00', '2018-02-01T20:00:00');

INSERT INTO public.delegations (registrar_id, domain_id, start_ts, end_ts) VALUES (1, 2, '2020-06-10T12:00:00', NULL);
INSERT INTO public.delegations (registrar_id, domain_id, start_ts, end_ts) VALUES (1, 3, '2010-03-01T09:00:00', '2019-02-20T14:00:00');

INSERT INTO public.delegations (registrar_id, domain_id, start_ts, end_ts) VALUES (2, 2, '2017-02-28T12:00:00', '2020-01-02T06:00:00');