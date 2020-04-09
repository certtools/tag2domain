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
-- Name: taxonomy; Type: TABLE; Schema: public; Owner: aaron
--

CREATE TABLE public.taxonomy (
    id integer NOT NULL,
    name character varying(300) NOT NULL,
    description text,
    is_actionable double precision,
    is_automatically_classifiable boolean,
    is_stable boolean,
    for_numbers boolean,
    for_domains boolean,
    url character varying(500),
    child_of integer
);


ALTER TABLE public.taxonomy OWNER TO aaron;

--
-- Name: taxonomy_id_seq; Type: SEQUENCE; Schema: public; Owner: aaron
--

CREATE SEQUENCE public.taxonomy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taxonomy_id_seq OWNER TO aaron;

--
-- Name: taxonomy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aaron
--

ALTER SEQUENCE public.taxonomy_id_seq OWNED BY public.taxonomy.id;


--
-- Name: taxonomy id; Type: DEFAULT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.taxonomy ALTER COLUMN id SET DEFAULT nextval('public.taxonomy_id_seq'::regclass);


--
-- Data for Name: taxonomy; Type: TABLE DATA; Schema: public; Owner: aaron
--

COPY public.taxonomy (id, name, description, is_actionable, is_automatically_classifiable, is_stable, for_numbers, for_domains, url, child_of) FROM stdin;
1	DHS CIIP	Dept. of Homeland Security Critical Infrastructure Sectors list	\N	\N	\N	t	t	https://github.com/MISP/misp-taxonomies/blob/master/dhs-ciip-sectors/machinetag.json	\N
2	RSIT	Reference Security Incident Taxonomy (previously "ENISA Taxonomy")	0.5	\N	t	t	t	https://github.com/MISP/misp-taxonomies/blob/master/dhs-ciip-sectors/machinetag.json	\N
3	DIT	Domain Industry Taxonomy (DIT)	\N	\N	t	f	t	https://rrdg.centr.org/projects/standards/domain-industry-taxonomy/	\N
4	Low content domain	RRDG low content domain taxonomy	\N	t	f	f	t	https://rrdg.centr.org/projects/current-projects/	\N
5	RRDG Registration Metrics	RRDG Registration Metrics Taxonomy	\N	t	f	f	t	\N	\N
\.


--
-- Name: taxonomy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aaron
--

SELECT pg_catalog.setval('public.taxonomy_id_seq', 1, false);


--
-- Name: taxonomy taxonomy_pkey; Type: CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.taxonomy
    ADD CONSTRAINT taxonomy_pkey PRIMARY KEY (id);


--
-- Name: taxonomy taxonomy_child_of_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.taxonomy
    ADD CONSTRAINT taxonomy_child_of_fkey FOREIGN KEY (child_of) REFERENCES public.taxonomy(id);


--
-- PostgreSQL database dump complete
--

