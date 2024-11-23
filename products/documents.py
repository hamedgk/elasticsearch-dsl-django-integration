from elasticsearch_dsl import (
        Document, Text, Date, Keyword, Integer, Nested, InnerDoc, Short, Index
)
from elasticsearch_dsl.connections import connections
from .utils.date import VariantFormatDate

connections.create_connection(hosts=['elasticsearch'], timeout=3, max_retries=15, retry_on_timeout=True)

class CategoryInnerDoc(InnerDoc):
    name = Text(fields={'keyword': Keyword()})

class ProductDocument(Document):
        name = Text(fields={'keyword': Keyword()})
        price = Integer()
        discount = Short()
        unit = Text(fields={'keyword': Keyword()})
        created_at = VariantFormatDate(format="yyyy-MM-dd HH:mm:ss||epoch_millis||strict_date_optional_time")
        updated_at = VariantFormatDate(format="yyyy-MM-dd HH:mm:ss||epoch_millis||strict_date_optional_time")
        categories = Nested(CategoryInnerDoc)
        class Index:
                name = 'products'
                settings = {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                }

        def json_serializable(self):
                return self.to_dict(skip_empty=False, include_meta=True)