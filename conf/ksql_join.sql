1)

create stream analyzed_text_tmp_stream (
		data STRUCT<
			identifier string, 
			headline string, 
			articleBody string, 
			dateCreated string, 
			dateModified string, 
			datePublished string, 
			publishDateEstimated string,
			url string,
			sourceDomain string,
			inLanguage string>
		) 
	with (kafka_topic='analyzed_text', value_format='JSON');

create stream "analyzed_text_flattened_tmp" with (partitions=1)
	AS SELECT
		data->identifier as "identifier",
		data as "data"
	FROM analyzed_text_tmp_stream;

create stream analyzed_text_final_stream (
		identifier string,
		data STRUCT<
			identifier string, 
			headline string, 
			articleBody string, 
			dateCreated string, 
			dateModified string, 
			datePublished string, 
			publishDateEstimated string,
			url string,
			sourceDomain string,
			inLanguage string>
		) 
	with (kafka_topic='analyzed_text_flattened_tmp', value_format='JSON');


2)

create stream analyzed_auth_org_tmp_stream (
		data STRUCT<
			identifier string, 
			authors array<string>, 
			publisher array<string>>
		) 
	with (kafka_topic='analyzed_auth_org', value_format='JSON');


create stream "analyzed_auth_org_flattened_tmp" with (partitions=1) 
	AS SELECT
		data->identifier as "identifier", 
		data as "data" 
	FROM analyzed_auth_org_tmp_stream;


create stream analyzed_auth_org_final_stream (
		identifier string,
		data STRUCT<
			identifier string, 
			authors array<string>, 
			publisher array<string>>
		) 
	with (kafka_topic='analyzed_auth_org_flattened_tmp', value_format='JSON');


3)

create stream analyzed_media_tmp_stream (
		data STRUCT<
            		identifier string,
            		contains array<string>>
		) 
	with (kafka_topic='analyzed_media', value_format='JSON');

create stream "analyzed_media_flattened_tmp" with (partitions=1) 
	AS SELECT
            	data->identifier as "identifier",
		data as "data"
	FROM analyzed_media_tmp_stream;


create stream analyzed_media_final_stream (
		identifier string,
		data STRUCT<
            		identifier string,
            		contains array<string>>
		) 
	with (kafka_topic='analyzed_media_flattened_tmp', value_format='JSON');


4)

create stream analyzed_ner_topic_tmp_stream (
		data STRUCT<
			identifier string, 
			about array<string>, 
			mentions array<string>,
			"topic" string>
		) 
	with (kafka_topic='analyzed_ner_topic', value_format='JSON');

create stream "analyzed_ner_topic_flattened_tmp" with (partitions=1) 
	AS SELECT
		data->identifier as "identifier",
		data as "data"
	FROM analyzed_ner_topic_tmp_stream;


create stream analyzed_ner_topic_final_stream (
		identifier string,
		data STRUCT<
			identifier string, 
			about array<string>, 
			mentions array<string>,
			"topic" string>
		) 
	with (kafka_topic='analyzed_ner_topic_flattened_tmp', value_format='JSON');





create stream NEW_join_tao with (partitions=1) as select t.identifier as identifier, t.data->headline as headline, t.data->articleBody as articleBody, t.data->dateCreated as dateCreated, t.data->dateModified as dateModified, t.data->datePublished as datePublished, t.data->publishDateEstimated as publishDateEstimated, t.data->url as url, t.data->sourceDomain as sourceDomain, t.data->inLanguage as inLanguage, ao.data->authors as authors, ao.data->publisher as publisher from analyzed_text_final_stream t inner join analyzed_auth_org_final_stream ao within 24 hours on t.identifier = ao.identifier;

create stream NEW_join_taont with (partitions=1) as select t.identifier as identifier, t.headline, t.articleBody, t.dateCreated, t.dateModified, t.datePublished, t.publishDateEstimated, t.url, t.sourceDomain, t.inLanguage, t.authors, t.publisher, nt.data->about as about, nt.data->mentions as mentions, nt.data->"topic" as "topic" from NEW_join_tao t inner join analyzed_ner_topic_final_stream nt within 24 hours on t.identifier = nt.identifier;

create stream "NEW_analyzed_article" with (partitions=1) as select t.identifier as "identifier", t.headline as "headline", t.articleBody as "articleBody", t.dateCreated as "dateCreated", t.dateModified as "dateModified", t.datePublished as "datePublished", t.publishDateEstimated as "publishDateEstimated", t.url as "url", t.sourceDomain as "sourceDomain", t.inLanguage as "inLanguage", t.authors as "authors", t.publisher as "publisher", t.about as "about", t.mentions as "mentions", t."topic" as "topic", m.data->contains as "contains" from NEW_join_taont t inner join analyzed_media_final_stream m within 24 hours on t.identifier = m.identifier;
