-- NOTE well: this view is a bit nic.at specific.
--   It is nevertheless given as a reference on how to link other tables (delegation2cluster in this example) to the taxonomy tables.

CREATE VIEW v_taxonomies_domains AS (
 SELECT 
    domains.domain_id,
    domains.domain_name,
    tags.tag_id,
    tags.tag_name,
    taxonomy.id as taxonomy_id,
    taxonomy.name as taxonomy_name
   FROM domains,
    delegations,
    delegation2cluster,
    clusters,
    clusters_tags,
    tags,
    taxonomy
  WHERE domains.domain_id = delegations.domain_id AND delegation2cluster.delegation_id = delegations.delegation_id AND clusters.cluster_id = delegation2cluster.cluster_id AND clusters_tags.cluster_id = clusters.cluster_id AND clusters_tags.tag_id = tags.tag_id AND taxonomy.id = tags.taxonomy_id
UNION
 SELECT 
    domains.domain_id,
    domains.domain_name,
    tags.tag_id,
    tags.tag_name,
    taxonomy.id as taxonomy_id,
    taxonomy.name as taxonomy_name
   FROM domains,
    domain_tags,
    tags,
    taxonomy
  WHERE domains.domain_id = domain_tags.domain_id AND domain_tags.tag_id = tags.tag_id AND taxonomy.id = tags.taxonomy_id AND domain_tags.taxonomy_id = 6
);
