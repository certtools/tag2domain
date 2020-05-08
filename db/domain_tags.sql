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
-- Name: domain_tags; Type: TABLE; Schema: public; Owner: aaron
--

CREATE TABLE public.domain_tags (
    domain_id integer,
    taxonomy_id integer,
    tag_id integer,
    value_id integer,
    measured_at timestamp with time zone DEFAULT now(),
    start_ts timestamp with time zone DEFAULT now(),
    end_ts timestamp with time zone DEFAULT now(),
    start_date integer,     
    end_date integer
);

COMMENT ON COLUMN domain_tags.measured_at IS 'The time of measurement when we can say this domain has this tag. Timestamp';
COMMENT ON COLUMN domain_tags.domain_id IS 'A link to a domains table. Adjust to your needs.';
COMMENT ON COLUMN domain_tags.start_ts IS 'Timestamp for an interval of validity. I.e: the tag is valid from start_ts till end_ts.';
COMMENT ON COLUMN domain_tags.end_ts IS 'See start_ts';
COMMENT ON COLUMN domain_tags.start_date IS 'Unix Epoch. Otherwise the same as start_ts';
COMMENT ON COLUMN domain_tags.end_date IS 'See start_date';


ALTER TABLE public.domain_tags OWNER TO aaron;

--
-- Data for Name: domain_tags; Type: TABLE DATA; Schema: public; Owner: aaron
--

COPY public.domain_tags (domain_id, taxonomy_id, tag_id, value_id, measured_at, start_ts, end_ts, start_date, end_date) FROM stdin;
\.


--
-- Name: domain_tags domain2label_domain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.domain_tags
    ADD CONSTRAINT domain2label_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES public.domains(domain_id);


--
-- Name: domain_tags domain2label_predicate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.domain_tags
    ADD CONSTRAINT domain2label_predicate_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id);


--
-- Name: domain_tags domain2label_taxonomy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.domain_tags
    ADD CONSTRAINT domain2label_taxonomy_id_fkey FOREIGN KEY (taxonomy_id) REFERENCES public.taxonomy(id);


--
-- Name: domain_tags domain2label_value_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY public.domain_tags
    ADD CONSTRAINT domain2label_value_id_fkey FOREIGN KEY (value_id) REFERENCES public.taxonomy_tag_val(id);


--
-- PostgreSQL database dump complete
--

