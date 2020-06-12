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


--
-- Name: tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: dwh_su
--

CREATE SEQUENCE public.tags_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tags_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dwh_su
--

ALTER SEQUENCE public.tags_tag_id_seq OWNED BY public.tags.tag_id;


--
-- Name: tags tag_id; Type: DEFAULT; Schema: public; Owner: dwh_su
--

ALTER TABLE ONLY public.tags ALTER COLUMN tag_id SET DEFAULT nextval('public.tags_tag_id_seq'::regclass);


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: aaron
--

COPY public.tags (tag_id, tag_name, taxonomy_id, tag_description, extras) FROM stdin;
1	PPC	4	\N	\N
2	For Sale	4	\N	\N
3	Under Construction Default Registrar/Hosting	4	\N	\N
4	Under Construction Individual Content	4	\N	\N
5	Expired Notice	4	\N	\N
6	Legal Notice	4	\N	\N
7	Download	4	\N	\N
8	Error: 400/500	4	\N	\N
9	Error: Software/Application Error Message	4	\N	\N
10	Can't Classify/Other	\N	\N	\N
11	Abusive	\N	\N	\N
12	Blank Page	4	\N	\N
13	DNS Failure	\N	\N	\N
14	Connection Failure	\N	\N	\N
15	robots.txt Forbidden	4	\N	\N
16	first name domain	4	\N	\N
17	RNDP	4	Registrar New domain page. Has a reference to a registrar.	\N
18	DFS	4	Domain for sale	\N
19	NDP	4	New domain page. No refernce to a registrar, generic templates.	\N
20	DEP	4	Domain expired/suspended	\N
21	UCP	4	Under construction page, showing a clear intention to develop a website.	\N
22	LEC	4	Law enforcement/confiscated	\N
23	WDP	4	Webserver default page	\N
24	EP	4	All kinds of error pages	\N
25	BLANK	4	Almost no content	\N
26	Frames	\N	Website uses a frame and is mostly unique content.	\N
27	Template	\N	Website uses a template and is mostly unique content.	\N
28	first_name	6	The domain name contains a first name	\N
\.



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


SELECT pg_catalog.setval('public.tags_tag_id_seq', 28, true);

--
-- PostgreSQL database dump complete
--

