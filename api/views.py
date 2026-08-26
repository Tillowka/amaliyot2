from django.shortcuts import render
from rest_framework import generics
from .serializer import ProductSerializer
from folder.models import Product
from rest_framework.views import APIView
from rest_framework.response import Response


class ProductList(APIView):
   def get(self,request):
       product = Product.objects.all()
       serializer = ProductSerializer(product,many=True)
       return Response(serializer.data)

# class CreateProductList(generics.CreateAPIView):
#     serializer_class = ProductSerializer
#     queryset = Product.objects.all()

class CreateProductList(APIView):
    def post(self,request):
        data = request.data
        serializer = ProductSerializer(data=data)
        try:
         if serializer.is_valid():
            serializer.save()

            return Response(
            {
                'status':True,
                'message':"yangi mahsulot qushildi"
            }
         )
        except:
           return Response(
                       {
                           'status':False,
                           'message':"Hato!"
                       }
                    )
        
class EditProductList(APIView):
    def put(self,request,pk):
       data = request.data
       product = Product.objects.get(pk=pk)
       
       try:
        serializer = ProductSerializer(product,data,partial=True)
        if serializer.is_valid():
          serializer.save()
          return Response(
                    {
                        'status':True,
                        'message':"Mahsulot yangilandi",
                        
                    }
                 )
       except:
          return Response(
                         {
                          'status':False,
                         'message':"Hato!"
                        }
                      )
          
class test(APIView):
    def post(self,request):
        print("Hello World!")

