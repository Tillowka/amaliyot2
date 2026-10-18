from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from folder.models import Product
from .serializer import ProductSerializer


class ProductList(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class CreateProductList(APIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'status': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = serializer.save()
        return Response(
            {
                'status': True,
                'message': 'Yangi mahsulot qoʻshildi',
                'id': product.pk,
            },
            status=status.HTTP_201_CREATED,
        )


class EditProductList(APIView):
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {'status': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            {'status': True, 'message': 'Mahsulot yangilandi'},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        return self.put(request, pk)


class test(APIView):
    def post(self, request):
        return Response({'status': True, 'message': 'Hello World!'})
