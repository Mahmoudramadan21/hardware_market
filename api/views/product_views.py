from django.shortcuts import render
import re

# rest-framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

# User model & serializers and models
from django.contrib.auth.models import User
from api.serializers import UserSerializer, UserSerializerWithToken, ProductSerializer
from api.models import *
# pagination
from django.core.paginator import Paginator, PageNotAnInteger, Page


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

#***************************************************************************#

# Get All Products
@api_view(['GET'])
def getProducts(request):
    try:
        query = request.query_params.get('q')
        if query is None:
            query = ''

        products = Product.objects.filter(
            name__icontains=query).order_by('-createdAt')

        page = request.query_params.get('page')
        paginator = Paginator(products, 4)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        if Page == None:
            page = 1

        serializer = ProductSerializer(products, many=True)
        return Response({'products': serializer.data, 'page': page, 'pages': paginator.num_pages})

    except:
        # Handle unexpected errors
        return Response('Unexpected error')


# Get Top Products
@api_view(['GET'])
def getTopProducts(request):
    try:
        products = Product.objects.filter(rating__gte=4).order_by('-rating')[0:5]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except:
        # Handle unexpected errors
        return Response('Unexpected error')

# Get a Product
@api_view(['GET'])
def getProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)

    except:
        # Handle unexpected errors
        return Response('Unexpected error')


@api_view(['GET'])
def getCategoryOfProducts(request, name):
    try:
        query = request.query_params.get('q', '')  # Use default value directly in get() method
        products = Product.objects.filter(category__icontains=name, name__icontains=query).order_by('-createdAt')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except:  # Catch specific exceptions if possible
        # Handle unexpected errors
        return Response('Unexpected error')


# Create a Product
@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'image', 'price', 'description', 'category', 'count-in-stock'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'image': openapi.Schema(type=openapi.TYPE_FILE),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'category': openapi.Schema(type=openapi.TYPE_STRING),
        'count-in-stock': openapi.Schema(type=openapi.TYPE_STRING),
    }
))
@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    try:
        user = request.user
        data = request.data

        product = Product.objects.create(
            user = user,
            name = data['name'],
            image = request.FILES.get('image'),
            price = data['price'],
            description = data['description'],
            category = data['category'],
            countInStock = data['count-in-stock'],
        )
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)

    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Update a Product
@swagger_auto_schema(method='put', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'image', 'price', 'description', 'category', 'count-in-stock'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'image': openapi.Schema(type=openapi.TYPE_FILE),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'category': openapi.Schema(type=openapi.TYPE_STRING),
        'count-in-stock': openapi.Schema(type=openapi.TYPE_STRING),
    }
))
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        data = request.data

        product.name = data['name']
        product.image = request.FILES.get('image')
        product.description = data['description']
        product.price = data['price']
        product.category = data['category']
        product.countInStock = data['count-in-stock']

        product.save()
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)

    except:
        # Handle unexpected errors
        return Response('Unexpected error')


# Delete a Product
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        product.delete()
        return Response('Product was deleted successfully')

    except:
        # Handle unexpected errors
        return Response('Unexpected error')


# Create a Product Review
@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['rating', 'comment'],
    properties={
        'rating': openapi.Schema(type=openapi.TYPE_INTEGER, format='int32'),
        'comment': openapi.Schema(type=openapi.TYPE_STRING),
    }
))
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    try:
        user = request.user
        product = Product.objects.get(id=pk)
        data = request.data

        # 1 - Review already exists
        alreadyExists = product.review_set.filter(user=user).exists()
        if alreadyExists:
            content = {'detail': 'Product already reviewed'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # 2 - No Rating or 0
        elif data['rating'] == 0:
            content = {'detail': 'Please select a rating'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # 3 - Create review
        else:
            review = Review.objects.create(
                user=user,
                product=product,
                name=user.first_name,
                rating=data['rating'],
                comment=data['comment'],
            )

            reviews = product.review_set.all()
            product.numOfReviews = len(reviews)

            total = 0
            for i in reviews:
                total += i.rating

            product.rating = total / len(reviews)
            product.save()

            return Response('Review Added')
    except:
        # Handle unexpected errors
        return Response('Unexpected error')
