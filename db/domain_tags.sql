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
-- Name: domain_tags; Type: TABLE; Schema: public; Owner: dwh_su
--

CREATE TABLE public.domain_tags (
    domain_id bigint,
    tag_id integer,
    taxonomy_id integer,
    value_id integer,
    measured_at timestamp with time zone DEFAULT now(),
    start_date integer,
    end_date integer,
    start_ts timestamp with time zone DEFAULT now(),
    end_ts timestamp with time zone
);



ALTER TABLE public.domain_tags OWNER TO dwh_su;

--
-- Name: COLUMN domain_tags.domain_id; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.domain_id IS 'A link to a domains table. Adjust to your needs.';


--
-- Name: COLUMN domain_tags.tag_id; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.tag_id IS 'Reference to a tag';


--
-- Name: COLUMN domain_tags.start_date; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.start_date IS 'Unix Epoch. Otherwise the same as start_ts';


--
-- Name: COLUMN domain_tags.end_date; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.end_date IS 'See start_date';


--
-- Name: COLUMN domain_tags.taxonomy_id; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.taxonomy_id IS 'Reference to a taxonomy';


--
-- Name: COLUMN domain_tags.value_id; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.value_id IS 'Reference to a value';


--
-- Name: COLUMN domain_tags.measured_at; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.measured_at IS 'The time of measurement when we can say this domain has this tag. Timestamp';


--
-- Name: COLUMN domain_tags.start_ts; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.start_ts IS 'Timestamp for an interval of validity. I.e: the tag is valid from start_ts till end_ts.';


--
-- Name: COLUMN domain_tags.end_ts; Type: COMMENT; Schema: public; Owner: dwh_su
--

COMMENT ON COLUMN public.domain_tags.end_ts IS 'See start_ts';


--
-- Name: idx_delegation_tags_delegation_id_0; Type: INDEX; Schema: public; Owner: dwh_su
--

CREATE INDEX idx_delegation_tags_delegation_id_0 ON public.domain_tags USING btree (domain_id);


--
-- Name: idx_delegation_tags_tag_id_0; Type: INDEX; Schema: public; Owner: dwh_su
--

CREATE INDEX idx_delegation_tags_tag_id_0 ON public.domain_tags USING btree (tag_id);


--
-- Name: idx_unique_flag; Type: INDEX; Schema: public; Owner: dwh_su
--

CREATE UNIQUE INDEX idx_unique_flag ON public.domain_tags USING btree (domain_id, tag_id, end_date);


--
-- Name: domain_tags fk_delegation_tags_0_domains; Type: FK CONSTRAINT; Schema: public; Owner: dwh_su
--

ALTER TABLE ONLY public.domain_tags
    ADD CONSTRAINT fk_delegation_tags_0_domains FOREIGN KEY (domain_id) REFERENCES public.domains(domain_id);


--
-- Name: domain_tags fk_delegation_tags_0_tags; Type: FK CONSTRAINT; Schema: public; Owner: dwh_su
--

ALTER TABLE ONLY public.domain_tags
    ADD CONSTRAINT fk_delegation_tags_0_tags FOREIGN KEY (tag_id) REFERENCES public.tags(tag_id);


--
-- Data for Name: domain_tags; Type: TABLE DATA; Schema: public; Owner: aaron
--

COPY public.domain_tags (domain_id, taxonomy_id, tag_id, value_id, measured_at, start_ts, end_ts, start_date, end_date) FROM stdin;
\.



--
-- PostgreSQL database dump complete
--

