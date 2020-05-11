--
-- PostgreSQL database dump
--

-- Dumped from database version 11.7
-- Dumped by pg_dump version 11.7

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
-- Name: tags; Type: TABLE; Schema: public; Owner: aaron
--

CREATE TABLE public.tags (
    tag_id integer NOT NULL PRIMARY KEY,
    tag_name character varying(500),
    taxonomy_id integer,
    tag_description character varying,
    extras jsonb
);


CREATE INDEX idx_tags_tag_name on tags(tag_name);

ALTER TABLE public.tags OWNER TO aaron;

--
-- Name: taxomoy_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: aaron
--

CREATE SEQUENCE public.taxomoy_tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taxomoy_tags_id_seq OWNER TO aaron;

--
-- Name: taxomoy_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aaron
--

ALTER SEQUENCE public.taxomoy_tags_id_seq OWNED BY public.tags.tag_id;


--
-- Name: tags id; Type: DEFAULT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.tags ALTER COLUMN tag_id SET DEFAULT nextval('public.taxomoy_tags_id_seq'::regclass);


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: aaron
--

COPY public.tags (tag_id, tag_name, taxonomy_id, tag_description, extras) FROM stdin;
10	Can't Classify/Other	\N	\N	\N
11	Abusive	\N	\N	\N
13	DNS Failure	\N	\N	\N
14	Connection Failure	\N	\N	\N
26	Frames	\N	Website uses a frame and is mostly unique content.	\N
27	Template	\N	Website uses a template and is mostly unique content.	\N
1	PPC	4	\N	\N
2	For Sale	4	\N	\N
3	Under Construction Default Registrar/Hosting	4	\N	\N
4	Under Construction Individual Content	4	\N	\N
5	Expired Notice	4	\N	\N
6	Legal Notice	4	\N	\N
7	Download	4	\N	\N
8	Error: 400/500	4	\N	\N
9	Error: Software/Application Error Message	4	\N	\N
12	Blank Page	4	\N	\N
15	robots.txt Forbidden	4	\N	\N
16	first name domain	4	\N	\N
17	RNDP	4	Registrar New domain page. Has a reference to a registrar.	\N
18	DFS	4	Domain for sale	\N
19	NDP	4	New domain page. No refernce to a registrar, generic templates.	\N
20	DEP	4	Domain expired/suspended	\N
21	UCP	4	Under construction page, showing a clear intention to develop a website.	\N
22	LEC	4	Law enforcement/confiscated	\N
24	EP	4	All kinds of error pages	\N
25	BLANK	4	Almost no content	\N
23	WDP	4	Webserver default page	\N
28	first_name	6	The domain name contains a first name	\N
\.


--
-- Name: taxomoy_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aaron
--

SELECT pg_catalog.setval('public.taxomoy_tags_id_seq', 1, false);


--
-- Name: tags taxonomy_predicates_pkey; Type: CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT taxonomy_predicates_pkey PRIMARY KEY (tag_id);


--
-- Name: tags taxonomy_predicates_taxonomy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT taxonomy_predicates_taxonomy_id_fkey FOREIGN KEY (taxonomy_id) REFERENCES public.taxonomy(id);


--
-- PostgreSQL database dump complete
--

