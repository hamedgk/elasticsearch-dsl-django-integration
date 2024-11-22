from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from elasticsearch_dsl import Q, Search, UpdateByQuery, Index
from django.utils.dateparse import parse_datetime

from .serializers import ProductSerializer
from .documents import ProductDocument
from .utils.date_helpers import (
    generate_datetime_now,
    generate_epoch_millis_now,
)

class ProductView(APIView):
    def get(self, request, pk=None):
        if pk:
            product = ProductDocument.get(id=pk)
            if not product:
                return Response({"error": "Product Not Found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(product.json_serializable())

        search = ProductDocument.search()
        name = request.query_params.get('name', None)
        unit = request.query_params.get('unit', None)
        #TODO validate using serializers

        if name or unit:
            query = Q('bool')
            if name:
                query &= Q('match', name=name)
            if unit:
                query &= Q('term', unit=unit)

            search = search.query(query)
        
        results = search.execute()
        products = [hit.json_serializable() for hit in results]
        return Response(products, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            now = generate_datetime_now()
            mill = generate_epoch_millis_now()
            product = ProductDocument(
                name=serializer.validated_data['name'],
                price=serializer.validated_data['price'],
                unit=serializer.validated_data['unit'],
                discount=serializer.validated_data['discount'],
                created_at=now,
                updated_at=mill,
            )
            product.save()
            return Response({"message": "Product created successfully", "id": product.meta.id}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = ProductDocument.get(id=pk)
            if not product:
                return Response({"error": "Product Not Found"}, status=status.HTTP_404_NOT_FOUND)
            product.name = serializer.validated_data['name']
            product.price = serializer.validated_data['price']
            product.unit = serializer.validated_data['unit']
            product.discount = serializer.validated_data['discount']
            product.updated_at = generate_datetime_now()
            product.save()
            return Response({"message": "Product updated successfully"}, status=status.HTTP_200_OK)
        
        except ProductDocument.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = ProductDocument.get(id=pk)
            if not product:
                return Response({"error": "Product Not Found"}, status=status.HTTP_404_NOT_FOUND)
            product.delete()
            return Response({"message": "Product deleted successfully"}, status=status.HTTP_200_OK)
        
        except ProductDocument.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class DiscountView(APIView):
    def patch(self, request):
        discount = request.data.get('discount', None)
        subject = request.data.get('subject', None)
        #TODO validate using serializers

        if not discount:
            return Response({"error": "discount is required"}, status=status.HTTP_400_BAD_REQUEST)

        ubq = UpdateByQuery(index=ProductDocument._index._name)

        ubq = ubq.query("nested", path="categories", query={
            "term": {
                "categories.name": subject
            }
        })

        ubq = ubq.script(
            source="""
            ctx._source.discount = params.discount;
            """,
            params={
                "discount": discount
            }
        )
        response = ubq.execute() 

        return Response(str(response))


class ProductIndexView(APIView):
    def post(self, request):
        idx = Index(name=ProductDocument.Index.name)
        if idx.exists():
            return Response("index already exists")
        else:
            ProductDocument.init()
            return Response("successfully created index")

    def delete(self, request):
        idx = Index(name=ProductDocument.Index.name)
        if idx.exists():
            response = idx.delete()
            return Response(str(response))
        else:
            return Response("index doesn't exists")

class CategoryView(APIView):
    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        category_name = request.data.get('name', None)
        #TODO validate using serializers
        if not category_name:
            return Response({"error": "category name is required"}, status=status.HTTP_400_BAD_REQUEST)
        ubq = UpdateByQuery(index=ProductDocument._index._name)
        ubq = ubq.query("term", _id=pk)
        ubq = ubq.script(
            source="""
            if (ctx._source.categories == null) {
                ctx._source.categories = [];
            }
            ctx._source.categories.add(['name': params.name]);
            """,
            params={
                "name": category_name
            }
        )
        response = ubq.execute()
        return Response(str(response))

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        category_name = request.data.get('name', None)
        if not category_name:
            return Response({"error": "category name is required"}, status=status.HTTP_400_BAD_REQUEST)
        #TODO validate using serializers
        ubq = UpdateByQuery(index=ProductDocument._index._name)
        ubq = ubq.query("term", _id=pk)
        ubq = ubq.script(
            source="""
                if (ctx._source.categories != null) {
                    ctx._source.categories.removeIf(cat -> cat.name == params.name);
                }
            """,
            params={
                "name": category_name
            }
        )
        response = ubq.execute()
        return Response(str(response))

class ProductAggregationView(APIView):
    def get(self, request, func=None):
        if not func:
            return Response({"error": "func is required"}, status=status.HTTP_400_BAD_REQUEST)
        if func not in ['avg', 'sum']:
            return Response({"error": "invalid function"}, status=status.HTTP_400_BAD_REQUEST)

        category_name = request.data.get('name', None)
        if not category_name:
            return Response({"error": "category name is required"}, status=status.HTTP_400_BAD_REQUEST)
        #TODO validate using serializers
        search = Search(index=ProductDocument._index._name)
        search = search.query("nested", path="categories", query={
            "term": {
                "categories.name": category_name
            }
        })
        match func:
            case "avg":
                search.aggs.metric('avg_price', 'avg', field='price')
                response = search.execute()
                avg_price = response.aggregations.avg_price.value if response.aggregations.avg_price.value is not None else 0
                return Response({"average_price": avg_price})
            case "sum":
                search.aggs.metric('sum_price', 'sum', field='price')
                response = search.execute()
                sum_price = response.aggregations.sum_price.value if response.aggregations.sum_price.value is not None else 0
                return Response({"sum_price": sum_price})
            case _:
                return Response({"error": "invalid function"}, status=status.HTTP_400_BAD_REQUEST)


class ProductTemporalView(APIView):
    def get(self, request):
        gte = request.query_params.get('gte', None)
        lte = request.query_params.get('lte', None)
        search = ProductDocument.search()

        if lte:
            parsed_lte = parse_datetime(lte)
            if not parsed_lte:
                return Response(
                    {"error": "Invalid date format. Use ISO 8601 (e.g., '2024-01-01T00:00:00Z')."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            search = search.filter('range', created_at={'lte': lte})

        if gte:
            parsed_gte = parse_datetime(gte)
            if not parsed_gte:
                return Response(
                    {"error": "Invalid date format. Use ISO 8601 (e.g., '2024-01-01T00:00:00Z')."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            search = search.filter('range', created_at={'gte': gte})

        results = search.execute()
        products = [hit.json_serializable() for hit in results]
        return Response(products, status=status.HTTP_200_OK)
