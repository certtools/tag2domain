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
    url character varying(500)
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
-- Name: taxonomy taxonomy_pkey; Type: CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.taxonomy
    ADD CONSTRAINT taxonomy_pkey PRIMARY KEY (id);


--
-- Name: TABLE taxonomy; Type: ACL; Schema: public; Owner: aaron
--

GRANT ALL ON TABLE public.taxonomy TO dwh_su;
GRANT SELECT ON TABLE public.taxonomy TO dwh_ro;


--
-- PostgreSQL database dump complete
--

