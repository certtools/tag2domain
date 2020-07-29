#!/usr/bin/env python

import sys
import csv

"""
Input format

alpha3-b,alpha2,English
aar,aa,Afar
abk,ab,Abkhazian
"""


r"""
Output format:
 COPY public.tags (tag_id, tag_name, taxonomy_id, tag_description, extras) FROM stdin;
 1 PPC 4   \N  \N
 2 For Sale    4   \N  \N
 3 Under Construction Default Registrar/Hosting    4   \N  \N
"""

id=29
taxonomy=7

with sys.stdin as infile:
    reader = csv.reader(infile, delimiter=',',)
    for row in reader:
        # print(row)
        print("%d\t%s\t%s\t%s\t\\N" %(id, row[1], taxonomy, row[2]))
        id += 1
