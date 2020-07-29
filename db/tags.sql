--
-- PostgreSQL database dump
--

-- Dumped from database version 11.7 (Debian 11.7-0+deb10u1)
-- Dumped by pg_dump version 11.7 (Debian 11.7-0+deb10u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: tags; Type: TABLE; Schema: public; Owner: dwh_su
--

CREATE TABLE public.tags (
    tag_id integer NOT NULL,
    tag_name character varying(200),
    tag_description character varying,
    taxonomy_id integer,
    extras jsonb
);


ALTER TABLE public.tags OWNER TO dwh_su;

--
-- Name: tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: dwh_su
--

CREATE SEQUENCE public.tags_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tags_tag_id_seq OWNER TO dwh_su;

--
-- Name: tags_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dwh_su
--

ALTER SEQUENCE public.tags_tag_id_seq OWNED BY public.tags.tag_id;


--
-- Name: tags tag_id; Type: DEFAULT; Schema: public; Owner: dwh_su
--

ALTER TABLE ONLY public.tags ALTER COLUMN tag_id SET DEFAULT nextval('public.tags_tag_id_seq'::regclass);


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: dwh_su
--

COPY public.tags (tag_id, tag_name, tag_description, taxonomy_id, extras) FROM stdin;
11	Abusive	\N	\N	\N
1	PPC	\N	4	\N
2	For Sale	\N	4	\N
3	Under Construction Default Registrar/Hosting	\N	4	\N
4	Under Construction Individual Content	\N	4	\N
5	Expired Notice	\N	4	\N
6	Legal Notice	\N	4	\N
7	Download	\N	4	\N
8	Error: 400/500	\N	4	\N
9	Error: Software/Application Error Message	\N	4	\N
12	Blank Page	\N	4	\N
15	robots.txt Forbidden	\N	4	\N
17	RNDP	Registrar New domain page. Has a reference to a registrar.	4	\N
18	DFS	Domain for sale	4	\N
19	NDP	New domain page. No refernce to a registrar, generic templates.	4	\N
20	DEP	Domain expired/suspended	4	\N
21	UCP	Under construction page, showing a clear intention to develop a website.	4	\N
22	LEC	Law enforcement/confiscated	4	\N
24	EP	All kinds of error pages	4	\N
25	BLANK	Almost no content	4	\N
23	WDP	Webserver default page	4	\N
29	Contains First Name	The domain name contains at least one first name	6	\N
30	Contains Male First Name	The domain name contains at least one male first name	6	\N
31	Contains Female First Name	The domain name contains at least one female first name	6	\N
26	Frames	Website uses a frame and is mostly unique content.	4	\N
27	Template	Website uses a template and is mostly unique content.	4	\N
10	Can't Classify/Other	\N	4	\N
13	DNS Failure	\N	4	\N
14	Connection Failure	\N	4	\N
\.


--
-- Name: tags_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dwh_su
--

SELECT pg_catalog.setval('public.tags_tag_id_seq', 28, true);


--
-- Name: tags idx_tag_name_unique_0; Type: CONSTRAINT; Schema: public; Owner: dwh_su
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT idx_tag_name_unique_0 UNIQUE (tag_name);


--
-- Name: tags pk_tags_tag_id; Type: CONSTRAINT; Schema: public; Owner: dwh_su
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT pk_tags_tag_id PRIMARY KEY (tag_id);


--
-- Name: tags taxonomy_predicates_taxonomy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dwh_su
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT taxonomy_predicates_taxonomy_id_fkey FOREIGN KEY (taxonomy_id) REFERENCES public.taxonomy(id);


--
-- Name: TABLE tags; Type: ACL; Schema: public; Owner: dwh_su
--

GRANT SELECT ON TABLE public.tags TO atbot;
GRANT SELECT ON TABLE public.tags TO dwh_ro;


--
-- PostgreSQL database dump complete
--

