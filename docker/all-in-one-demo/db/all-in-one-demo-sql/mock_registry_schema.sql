CREATE SEQUENCE domain_seq;

CREATE TABLE public.domains
(
    domain_id bigint NOT NULL DEFAULT nextval('domain_seq'::regclass),
    domain_name character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT pk_domains PRIMARY KEY (domain_id),
    CONSTRAINT idx_domains_domain_name UNIQUE (domain_name)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

CREATE SEQUENCE registrar_seq;
CREATE TABLE public.registrars
(
    registrar_id bigint NOT NULL DEFAULT nextval('registrar_seq'::regclass),
    registrar_name character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT pk_registrars PRIMARY KEY (registrar_id),
    CONSTRAINT idx_registrars_registrar_name UNIQUE (registrar_name)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

CREATE SEQUENCE delegation_seq;
CREATE TABLE public.delegations
(
    delegation_id bigint NOT NULL DEFAULT nextval('delegation_seq'::regclass),
    registrar_id bigint NOT NULL,
    domain_id bigint NOT NULL,
    start_ts timestamp with time zone NOT NULL,
    end_ts timestamp with time zone,
    CONSTRAINT pk_delegations PRIMARY KEY (delegation_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE ONLY public.delegations ADD CONSTRAINT fk_delegations_registrar FOREIGN KEY (registrar_id) REFERENCES registrars(registrar_id);
ALTER TABLE ONLY public.delegations ADD CONSTRAINT fk_delegations_domain FOREIGN KEY (domain_id) REFERENCES domains(domain_id);