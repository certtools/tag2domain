CREATE SCHEMA IF NOT EXISTS tag2domain;
SET search_path TO tag2domain;

CREATE SEQUENCE public.domain_seq;
CREATE TABLE public.domains
(
    domain_id bigint NOT NULL DEFAULT nextval('public.domain_seq'::regclass),
    domain_name character varying(100) COLLATE pg_catalog."default",
    pdo character varying(10) COLLATE pg_catalog."default",
    u_label character varying(100) COLLATE pg_catalog."default",
    isidn boolean DEFAULT false,
    split boolean DEFAULT false,
    CONSTRAINT pk_domains PRIMARY KEY (domain_id),
    CONSTRAINT idx_domains_domain_name UNIQUE (domain_name)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

CREATE SEQUENCE public.registrar_seq;
CREATE TABLE public.registrars
(
    registrar_id bigint NOT NULL DEFAULT nextval('public.registrar_seq'::regclass),
    registrar_name character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT pk_registrars PRIMARY KEY (registrar_id),
    CONSTRAINT idx_registrars_registrar_name UNIQUE (registrar_name)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

CREATE TABLE domain_tags
(
    domain_id bigint,
    tag_id integer,
    start_date integer,
    end_date integer,
    taxonomy_id integer,
    value_id integer,
    measured_at timestamp with time zone DEFAULT now(),
    start_ts timestamp with time zone DEFAULT now(),
    end_ts timestamp with time zone,
    producer character varying(100) COLLATE pg_catalog."default" DEFAULT NULL,
    CONSTRAINT fk_delegation_tags_0_domains FOREIGN KEY (domain_id)
        REFERENCES public.domains (domain_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_delegation_tags_0_tags FOREIGN KEY (tag_id)
        REFERENCES tags (tag_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

CREATE SEQUENCE public.delegation_seq;

CREATE TABLE public.delegations
(
    delegation_id bigint NOT NULL DEFAULT nextval('public.delegation_seq'::regclass),
    domain_id bigint NOT NULL,
    registrar_id bigint NOT NULL,
    create_date integer,
    create_time time without time zone,
    purge_date integer,
    purge_time time without time zone,
    stichtag timestamp without time zone,
    price_class bigint,
    website_category_id bigint,
    ry_del_id bigint,
    create_ts timestamp without time zone,
    purge_ts timestamp without time zone,
    delegation_period tsrange,
    CONSTRAINT pk_delegations_0 PRIMARY KEY (delegation_id),
    CONSTRAINT idx_delegations_unique_0 UNIQUE (domain_id, create_date, create_time),
    CONSTRAINT fk_delegations_domains FOREIGN KEY (domain_id)
        REFERENCES public.domains (domain_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

CREATE TABLE delegation_tags
(
    delegation_id bigint,
    tag_id integer,
    start_date integer,
    end_date integer,
    taxonomy_id integer,
    value_id integer,
    measured_at timestamp with time zone DEFAULT now(),
    start_ts timestamp with time zone DEFAULT now(),
    end_ts timestamp with time zone DEFAULT now(),
    producer character varying(100) COLLATE pg_catalog."default" DEFAULT NULL,
    CONSTRAINT fk_delegation_tags_delegations FOREIGN KEY (delegation_id)
        REFERENCES public.delegations (delegation_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_delegation_tags_tags FOREIGN KEY (tag_id)
        REFERENCES tags (tag_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


CREATE TABLE intersections
(
    intxn_id bigint,
    pickerl_id integer,
    datum_start integer,
    datum_ende integer,
    taxonomie_id integer,
    beschriftung_id integer,
    gemessen_um timestamp with time zone DEFAULT now(),
    zeitstempel_start timestamp with time zone DEFAULT now(),
    zeitstempel_ende timestamp with time zone DEFAULT now(),
    erzeuger character varying(100) COLLATE pg_catalog."default" DEFAULT NULL,
    CONSTRAINT fk_intersection_tags_tags FOREIGN KEY (pickerl_id)
        REFERENCES tags (tag_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;