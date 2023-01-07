from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from product.models import *
from rest_framework_simplejwt.tokens import RefreshToken


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


# for jwt auth
class TestCaseBase(APITestCase):
    @property
    def bearer_token(self):
        # assuming there is a user in User model
        user = User.objects.create_user(
            email='test@gmail.com', password='testpass'
        )

        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}





class TestCategoryAPI(TestCaseBase):

    def test_create_category(self):
        url = reverse('api:category-list-create')
        data = {
            'name': 'Test Category'
        }

        # Send a POST request to the category view to create a new category        
        response = client.post(url, data=data, format='json', **self.bearer_token)

        # Check the response status code and content
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'id': 1, 'name': 'Test Category'})

        # Check that the category was created in the database
        category = Category.objects.get(id=1)
        self.assertEqual(category.name, 'Test Category')



    def test_retrieve_category(self):
        category = Category.objects.create(name='Test Category')
        url = reverse('api:category-retrive-update-destroy', kwargs={'pk':category.pk})
        
        # Send a GET request to the category view to retrieve the category
        response = client.get(url, **self.bearer_token)

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Category')



    def test_update_category(self):
        # Create a category in the database
        category = Category.objects.create(name='Test Category')
        url = reverse('api:category-retrive-update-destroy', kwargs={'pk':category.pk})
        # Send a PUT request to the category view to update the category
        data = {
            'name': 'Updated Category'
        }
        response = client.put(url, data=data, format='json', **self.bearer_token)

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'id': category.id, 'name': 'Updated Category'})

        # Check that the category was updated in the database
        category = Category.objects.get(id=category.id)
        self.assertEqual(category.name, 'Updated Category')


    
    def test_delete_category(self):
        # Create a category in the database
        category = Category.objects.create(name='Test Category')
        url = reverse('api:category-retrive-update-destroy', kwargs={'pk':category.pk})

        # Send a DELETE request to the category view to delete the category
        response = client.delete(url, **self.bearer_token)

        # Check the response status code and content
        self.assertEqual(response.status_code, 204)

        # Check that the category was deleted from the database
        self.assertEqual(Category.objects.count(), 0)






class TestProductAPI(TestCaseBase):
    def setUp(self):
        self.cat = Category.objects.create(
            name = "test_category"
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            price=100,
            rank=4,
            category=self.cat
        )
    
    def test_create_product(self):
        url = reverse('api:product-create')

        data = {
            'name': 'Test Product',
            'price': 100,
            'category': self.cat.id,
            'rank': 3,

        }
        response = client.post(url, data=data, format='json', **self.bearer_token)

        # Check the response status code and content
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['rank'], 3)

        # Check that the product was created in the database
        product = Product.objects.get(id=1)
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 100)


    def test_retrieve_product(self):
        
        url = reverse('api:product-detail', kwargs={'pk':self.product.pk})
        

        # Send a GET request to the product view to retrieve the product
        response = client.get(url, **self.bearer_token)

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['category'], self.cat.name)

    def test_update_product(self):
        
        url = reverse('api:product-update', kwargs={'pk':self.product.pk})

        # Send a PUT request to the product view to update the product
        data = {
            'name': 'Updated Product',
            'price': 200,
            'category':self.cat.id,
            'rank':20
        }
        response = client.put(url, data=data, format='json', **self.bearer_token)

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated Product')

        # Check that the product was updated in the database
        product = Product.objects.get(id=self.product.id)
        self.assertEqual(product.name, 'Updated Product')
        self.assertEqual(product.price, 200)

    def test_delete_product(self):
        url = reverse('api:product-delete', kwargs={'pk':self.product.pk})

        # Send a DELETE request to the product view to delete the product
        response = client.delete(url, **self.bearer_token)

        # Check the response status code and content
        self.assertEqual(response.status_code, 204)

        # Check that the product was deleted from the database
        self.assertEqual(Product.objects.count(), 0)
