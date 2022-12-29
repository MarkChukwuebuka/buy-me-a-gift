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
import base64 as bs6


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
        print(user)
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




# class RequestPasswordReset(GenericAPIView):
#     serializer_class = ResetPasswordRequestSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)

#         email = request.data['email']
#         if User.objects.filter(email=email).exists():
#             user = User.objects.get(email=email)
#             uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
#             token = PasswordResetTokenGenerator().make_token(user)
#             current_site = get_current_site(request=request).domain
#             relativeLink = reverse("password-reset-confirm", kwargs={'uidb64': uidb64, 'token': token})
#             absurl = 'http://' + current_site + relativeLink
#             # email_body = 'Hello, \n Use link below to reset your password  \n' + \
#             #              absurl
#             # data = {'email_body': email_body, 'to_email': user.email,
#             #         'email_subject': 'Reset your passsword'}
#             # sent_mail(data)
#             return Response({'success': absurl}, status=status.HTTP_200_OK)
#         else:
#             return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)



# class PasswordTokenCheckAPI(GenericAPIView):

#     def get(self, request, uidb64, token):
#         try:
#             id = smart_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(id=id)
#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 return Response({'error': 'Token is not valid, please request a new one '}, status=status.HTTP_400_BAD_REQUEST)
#             return Response({
#                 'success': True,
#                 'message': 'credential valid',
#                 'uidb64': uidb64,
#                 'token': token
#             })
#         except DjangoUnicodeDecodeError as identifier:
#             return Response({'error': 'Token is not valid, please request a new one '}, status=status.HTTP_400_BAD_REQUEST)


# class SetNewPasswordAPIView(GenericAPIView):
#     serializer_class = SetNewPasswordSerializer
#     def put(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)





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



# class WishListView(mixins.CreateModelMixin, ListAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = WishListSerializer
#     queryset = WishList.objects.all()

#     def perform_create(self, serializer):
#         user = self.request.user
#         products = self.request.data.get('products')

#         for product in products:
#             category = Product.objects.get(id=product).category

#             if not WishList.objects.filter(user=user, category=category).exists():
#                 serializer.save(user=user, product=product, category=category)
#             else:
#                 raise ValidationError('You can only add one product from each category.')


# class WishlistCreateAPIView(CreateAPIView):
#     permission_classes = (AllowAny,)
#     queryset = WishList.objects.all()
#     serializer_class = WishListCreateSerializer


# class WishListProductListView(views.APIView):
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):

#         user = request.user

#         # Get the wishlist ID and ordering fields from the request
#         wishlist_id = request.GET.get('wishlist_id')
#         ordering = request.GET.get('ordering')
        
#         # Split the ordering fields into a list
#         ordering_fields = ordering.split(',') if ordering else []
        
#         # Get the wishlist and its products from the database, sorted by the ordering fields
#         wishlist = WishList.objects.get(user=user)
#         products = wishlist.products.all().order_by(*ordering_fields)
        
#         # Serialize the products using a serializer
#         serializer = ProductSerializer(products, many=True)
        
#         # Return a response with the serialized data
#         return Response({'products': serializer.data})




# class WishListProductListViewByIdentifier(views.APIView):
#     permission_classes = (AllowAny,)

#     def get(self, request):
        
#         user = User

#         # Get the wishlist ID and ordering fields from the request
#         wishlist_id = request.GET.get('wishlist_id')
#         ordering = request.GET.get('ordering')
        
#         # Split the ordering fields into a list
#         ordering_fields = ordering.split(',') if ordering else []
        
#         # Get the wishlist and its products from the database, sorted by the ordering fields
#         wishlist = WishList.objects.get(user=user)
#         products = wishlist.products.all().order_by(*ordering_fields)
        
#         # Serialize the products using a serializer
#         serializer = ProductSerializer(products, many=True)
        
#         # Return a response with the serialized data
#         return Response({'products': serializer.data})
