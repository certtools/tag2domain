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
-- Name: taxonomy_tag_val; Type: TABLE; Schema: public; Owner: aaron
--

CREATE TABLE public.taxonomy_tag_val (
    id integer NOT NULL,
    value text,
    value_float float,
    value_bool boolean,
    value_int integer,
    tag_id integer
);


CREATE UNIQUE INDEX idx_taxonomy_tag_val_id on taxonomy_tag_val (tag_id, value);


ALTER TABLE public.taxonomy_tag_val OWNER TO aaron;


--
-- Name: taxonomy_tag_val_id_seq; Type: SEQUENCE; Schema: public; Owner: aaron
--

CREATE SEQUENCE public.taxonomy_tag_val_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taxonomy_tag_val_id_seq OWNER TO aaron;

--
-- Name: taxonomy_tag_val_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aaron
--

ALTER SEQUENCE public.taxonomy_tag_val_id_seq OWNED BY public.taxonomy_tag_val.id;


--
-- Name: taxonomy_tag_val id; Type: DEFAULT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.taxonomy_tag_val ALTER COLUMN id SET DEFAULT nextval('public.taxonomy_tag_val_id_seq'::regclass);


--
-- Data for Name: taxonomy_tag_val; Type: TABLE DATA; Schema: public; Owner: aaron
--

COPY public.taxonomy_tag_val (id, value, tag_id) FROM stdin;
\.


--
-- Name: taxonomy_tag_val_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aaron
--

SELECT pg_catalog.setval('public.taxonomy_tag_val_id_seq', 1, false);


--
-- Name: taxonomy_tag_val taxonomy_tag_val_pkey; Type: CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.taxonomy_tag_val
    ADD CONSTRAINT taxonomy_tag_val_pkey PRIMARY KEY (tag_id);


--
-- Name: taxonomy_tag_val taxonomy_tag_val_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.taxonomy_tag_val
    ADD CONSTRAINT taxonomy_tag_val_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(tag_id);


--
-- PostgreSQL database dump complete
--

