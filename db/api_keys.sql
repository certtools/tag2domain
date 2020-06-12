--
-- PostgreSQL database dump
--

-- Dumped from database version 10.13 (Debian 10.13-1.pgdg100+1)
-- Dumped by pg_dump version 10.13 (Debian 10.13-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: api_keys; Type: TABLE; Schema: public; Owner: aaron
--

CREATE TABLE public.api_keys (
    email character varying(100) NOT NULL,
    api_key character varying(128),
    expires timestamp with time zone DEFAULT (now() + '28 days'::interval)
);



--
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (email);


--
-- Name: TABLE api_keys; Type: ACL; Schema: public; Owner: aaron
--



--
