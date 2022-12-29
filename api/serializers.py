from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model
from product.models import *
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize CustomUser model.
    """

    class Meta:
        model = User
        fields = ("id", "email")



class SignupSerializer(serializers.ModelSerializer):

    """
    Serializer class to serialize registration requests and create a new user.

    """

    class Meta:
        model = User
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class LoginSerializer(serializers.Serializer):

    """
    Serializer class to authenticate users with email and password.

    """

    class Meta:
        model = User
        fields = ("email", "password")


    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=128)
    re_new_password = serializers.CharField(max_length=128)

    def validate(self, data):
        if data["new_password"] != data["re_new_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data



class ProductListSerializer(serializers.ModelSerializer):

    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = (
            
            'name',
            'category',
            'price',
            'created_time',
            'rank'           
        )


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'name',
            'price',
            'category',
            'rank',

        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class WishListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = WishList
        fields = '__all__'

    # products = serializers.ListField(child=ProductSerializer())

    def validate(self, data):
        categories = set()
        for product in data['products']:
            category = product['category']
            if category in categories:
                raise serializers.ValidationError(
                    "You can only add one product from each category to the wishlist"
                )
            categories.add(category)
        return data




class WishListSerializer(serializers.Serializer):
    products = serializers.ListField(child=ProductSerializer())

    def validate(self, data):
        categories = set()
        for product in data['products']:
            category = product['category']
            if category in categories:
                raise serializers.ValidationError(
                    "You can only add one product from each category to the wishlist"
                )
            categories.add(category)
        return data
