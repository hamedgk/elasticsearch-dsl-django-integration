from elasticsearch_dsl import (
        Document, Text, Date, Keyword, Integer, Nested, InnerDoc, Short, Index
)
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['elasticsearch'], timeout=3, max_retries=15, retry_on_timeout=True)

class CategoryInnerDoc(InnerDoc):
    name = Text(fields={'keyword': Keyword()})

class ProductDocument(Document):
        name = Text(fields={'keyword': Keyword()})
        price = Integer()
        discount = Short()
        unit = Text(fields={'keyword': Keyword()})
        created_at = Date()
        updated_at = Date()
        categories = Nested(CategoryInnerDoc)
        class Index:
                name = 'products'
                settings = {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                }

        def json_serializable(self):
                return self.to_dict(skip_empty=False, include_meta=True)