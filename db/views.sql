-- NOTE well: this view is a bit nic.at specific.
--   It is nevertheless given as a reference on how to link other tables (delegation2cluster in this example) to the taxonomy tables.

CREATE OR REPLACE VIEW v_taxonomies_domains AS (
( SELECT domains.domain_id,
    domains.domain_name,
    tags.tag_id,
    tags.tag_name,
    taxonomy.id AS taxonomy_id,
    taxonomy.name AS taxonomy_name,
    delegation2cluster.start_time,
    delegation2cluster.end_time,
	'{}' values_array
   FROM domains,
    delegations,
    delegation2cluster,
    clusters,
    clusters_tags,
    tags,
    taxonomy
  WHERE
    domains.domain_id = delegations.domain_id AND
    delegation2cluster.delegation_id = delegations.delegation_id AND
    clusters.cluster_id = delegation2cluster.cluster_id AND
    clusters_tags.cluster_id = clusters.cluster_id AND
    clusters_tags.tag_id = tags.tag_id AND
    taxonomy.id = tags.taxonomy_id AND
    taxonomy.id = 4   -- we are currently pinning this to Low Content Domains
)
UNION
( SELECT domains.domain_id,
    domains.domain_name,
    tags.tag_id,
    tags.tag_name,
    taxonomy.id AS taxonomy_id,
    taxonomy.name AS taxonomy_name,
	delegation_tags.start_ts as start_time,
	delegation_tags.end_ts as end_time,
	'{}' values_array
 FROM
    domains,
    delegations,
    delegation_tags,
    tags,
    taxonomy
 WHERE
    domains.domain_id = delegations.domain_id AND
    delegation_tags.delegation_id = delegations.delegation_id AND
    delegation_tags.tag_id = tags.tag_id AND
    taxonomy.id = tags.taxonomy_id 
)
UNION
( SELECT domains.domain_id,
    domains.domain_name,
    tags.tag_id,
    tags.tag_name,
    taxonomy.id AS taxonomy_id,
    taxonomy.name AS taxonomy_name,
    domain_tags.start_ts as start_time,
    domain_tags.end_ts as end_time,
	'{}' values_array
   FROM domains,
    domain_tags,
    tags,
    taxonomy
  WHERE
    domains.domain_id = domain_tags.domain_id AND
    domain_tags.tag_id = tags.tag_id AND
    taxonomy.id = tags.taxonomy_id AND
    taxonomy.id not in (4) 			-- exclude potential low content. These are covered above
)
ORDER BY domain_name
);			
