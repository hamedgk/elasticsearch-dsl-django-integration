from rest_framework import serializers

class CategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20)

class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    price = serializers.IntegerField(min_value=1)
    discount = serializers.IntegerField(min_value=0, max_value=100)
    unit = serializers.CharField(max_length=50)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        depth = 1