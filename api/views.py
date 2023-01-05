from django.contrib.auth import get_user_model
from rest_framework import status, views, mixins
from rest_framework.generics import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from .serializers import *
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import permission_classes, api_view


User = get_user_model()



class SignupAPIView(GenericAPIView):

    """
    An endpoint for the client to create a new User.
    """

    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}

        wishlist = WishList()
        wishlist.user = user
        wishlist.save()

        return Response(data, status=status.HTTP_201_CREATED)




class LoginAPIView(GenericAPIView):

    """
    An endpoint to authenticate existing users using their email and password.
    """

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        authenticate(user)
        login(request, user)
        serializer = UserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        
        return Response(data, status=status.HTTP_200_OK)





class LogoutAPIView(GenericAPIView):

    """
    An endpoint to logout users.

    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)





class PasswordResetView(CreateAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Email address not found."}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            return Response({"detail": "User is inactive."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        password_reset_url =f"http://localhost:8000/api/password-reset-confirm/{uid}/{token}/"

        # password_reset_url = reverse("password-reset-confirm", kwargs={"uidb64": uid, "token": token})

        # send_mail(
        #     "Password reset",
        #     f"Use the following link to reset your password: {password_reset_url}",
        #     "from@example.com",
        #     [email],
        #     fail_silently=False,
        # ) 
        return Response({"Mesage": password_reset_url}, status=status.HTTP_200_OK)



class PasswordResetConfirmView(CreateAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = kwargs["uidb64"]
        
        token = kwargs["token"]
        
        try:
            uid = urlsafe_base64_decode(uid).decode()
            
            user = User.objects.get(pk=uid)
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid password reset token."}, status=status.HTTP_400_BAD_REQUEST)




class ProductListAPIView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        price_gt = self.request.query_params.get('price_gt')
        price_lt = self.request.query_params.get('price_lt')
        if price_gt:
            queryset = queryset.filter(price__gt=price_gt)
        if price_lt:
            queryset = queryset.filter(price__lt=price_lt)
        return queryset


class ProductDetailAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDeleteAPIView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductUpdateAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductCreateAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryCreateAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDeleteAPIView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryListAPIView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class WishlistByIdentifierView(views.APIView):

    permission_classes = (AllowAny,)
    
    def get_object(self, pk):
       
        try:
            return WishList.objects.get(user__email=pk)
        except WishList.DoesNotExist:
            raise Http404


    def get(self, request, user, format=None):
    
        wishlist = self.get_object(user)
        serializer = WishlistByIdentifierSerializer(wishlist)
        return Response(serializer.data)




class WishlistView(RetrieveUpdateDestroyAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj



class WishlistProductDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = WishList.objects.all()

    def get_object(self):       
        try:
            return WishList.objects.get(user=self.request.user)
        except WishList.DoesNotExist:
            raise Http404

    def put(self, instance, pk):
        
        wishlist = self.get_object()
        product = Product.objects.get(pk=pk)
        products = wishlist.products
        products.remove(product)
        wishlist.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

