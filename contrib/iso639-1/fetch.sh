#!/bin/sh

OUT=language-codes.csv
url=https://datahub.io/core/language-codes/r/language-codes-3b2.csv

wget -O $OUT $url

# Input format
# 
#alpha3-b,alpha2,English
#aar,aa,Afar
#abk,ab,Abkhazian


# Output format:
# COPY public.tags (tag_id, tag_name, taxonomy_id, tag_description, extras) FROM stdin;
# 1	PPC	4	\N	\N
# 2	For Sale	4	\N	\N
# 3	Under Construction Default Registrar/Hosting	4	\N	\N
tail  -n +2 $OUT | python convert.py

