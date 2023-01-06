from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from product.models import *

User = get_user_model()
client = APIClient()


# Create your tests here.

class TestSignupAPI(APITestCase):
    def setUp(self):
        self.url = reverse('api:signup')

    def test_signup(self):
        # Send a POST request to the signup view
        data = {
            'email': 'testuser@gmail.com',
            'password': 'testpass'
        }
        response = client.post(self.url, data=data, format='json')

        # Check the response status code and content
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['email'], 'testuser@gmail.com')

        # Check that the user was created in the database

        user = User.objects.get(email=response.data['email'])
        self.assertEqual(user.email, 'testuser@gmail.com')
        self.assertEqual(User.objects.all().count(), 1)


class TestLoginAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@gmail.com',
            password='testpass'
        )
        self.url = reverse('api:login')

    def test_login(self):
        # Send a POST request to the login view
        data = {
            'email': 'test@gmail.com',
            'password': 'testpass'
        }
        response = client.post(self.url, data=data, format='json')

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@gmail.com')
        # check if user gets authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)




class TestCategoryAPI(APITestCase):
    def setUp(self):
    
        self.user = User.objects.create_user(
            email='test@gmail.com',
            password='testpass'
        )
        client.login(email='test@gmail.com', password='testpass')

    def test_create_category(self):
        # Send a POST request to the category view to create a new category
        url = reverse('api:category-list-create')
        data = {
            'name': 'Test Category'
        }
        response = client.post(url, data=data, format='json')

        # Check the response status code and content
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'id': 1, 'name': 'Test Category'})

        # Check that the category was created in the database
        category = Category.objects.get(id=1)
        self.assertEqual(category.name, 'Test Category')

    def test_retrieve_category(self):
        url = reverse('api:category-retrive-update-destroy', kwargs={'pk':1})

        # Create a category in the database
        Category.objects.create(name='Test Category')

        # Send a GET request to the category view to retrieve the category
        response = client.get(url)

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'id': 1, 'name': 'Test Category'})

    # def test
































# class TestProductAPI(APITestCase):
#     def setUp(self):
        
#         self.user = User.objects.create_user(
#             email='test@gmail.com',
#             password='testpass'
#         )
#         client.login(email='test@gmail.com', password='testpass')

#     def test_create_product(self):
#         url = reverse('api:product-create')
#         # Send a POST request to the product view to create a new product
#         cat = Category.objects.create(
#             name = "test_category"
#         )

#         data = {
#             'name': 'Test Product',
#             'price': 100,
#             'rank': 1,
#             'category':1

#         }
#         response = client.post(url, data=data, format='json')

#         # Check the response status code and content
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data, {'id': 1, 'name': 'Test Product', 'price': 100})

#         # Check that the product was created in the database
#         product = Product.objects.get(id=1)
#         self.assertEqual(product.name, 'Test Product')
#         self.assertEqual(product.price, 100)

#     def test_retrieve_product(self):
#         # Create a product in the database
#         Product.objects.create(name='Test Product', price=100)

#         # Send a GET request to the product view to retrieve the product
#         response = self.client.get('/products/1/')

#         # Check the response status code and content
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data, {'id': 1, 'name': 'Test Product', 'price': 100})

#     def test_update_product(self):
#         # Create a product in the database
#         Product.objects.create(name='Test Product', price=100)

#         # Send a PUT request to the product view to update the product
#         data = {
#             'name': 'Updated Product',
#             'price': 200
#         }
#         response = self.client.put('/products/1/', data=data, format='json')

#         # Check the response status code and content
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data, {'id': 1, 'name': 'Updated Product', 'price': 200})

#         # Check that the product was updated in the database
#         product = Product.objects.get(id=1)
#         self.assertEqual(product.name, 'Updated Product')
#         self.assertEqual(product.price, 200)

#     def test_delete_product(self):
#         # Create a product in the database
#         Product.objects.create(name='Test Product', price=100)

#         # Send a DELETE request to the product view to delete the product
#         response = self.client.delete('/products/1/')

#         # Check the response status code and content
#         self.assertEqual(response.status_code, 204)

#         # Check that the product was deleted from the database
#         self.assertEqual(Product.objects.count(), 0)
