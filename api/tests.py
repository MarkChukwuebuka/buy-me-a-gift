from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from product.models import *
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()
client = APIClient()



# test for signup endpoint
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




# test for login endpoints
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
        
        user = User.objects.create_user(
            email='test@gmail.com', password='testpass'
        )

        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}







# tests for category endpoints
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







# tests for product endpoints
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

    def test_partial_update_product(self):
        
        url = reverse('api:product-update', kwargs={'pk':self.product.pk})

        # Send a Patch request to the product view to update the product
        data = {
            'name': 'Updated Product',
            'price': 200,
            'category':self.cat.id,
            # 'rank':20
        }
        response = client.patch(url, data=data, format='json', **self.bearer_token)

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




# test for get wishlist by identifier
class TestGetWishlistByIdentifier(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@gmail.com', password='testpass'
        )
        self.wishlist = WishList.objects.create(
            user=self.user
        )
        self.url = reverse('api:wishlist-view-by-identifier', kwargs={'user':self.user.email})

    def test_wishlist_by_identifier(self):
        response = client.get(self.url)

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user'], 'test@gmail.com')




class TestWishListAPI(TestCaseBase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@gmail.com', password='testpass'
        )

        token_response = self.client.post(
            reverse('api:login'),
            data={'email': 'test@gmail.com', 'password': 'testpass'},
            format='json'
        )
        self.access_token = token_response.data['tokens']['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.wishlist = WishList.objects.create(
            user=self.user
        )

        self.cat1= Category.objects.create(
            name = "test_category"
        )

        self.cat2= Category.objects.create(
            name = "test_category2"
        )

        self.product1 = Product.objects.create(
            name = "test_product1",
            price = 5.00,
            rank = 2,
            category = self.cat1,
        )

        self.product2 = Product.objects.create(
            name = "test_product2",
            price = 50.00,
            rank = 23,
            category = self.cat2,
        )

    def test_retrieve_wishlist(self):
        url = reverse('api:wishlist')
        
        response = self.client.get(url)

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['products'], [])


    def test_add_product_to_wishlist(self):
        url = reverse('api:wishlist')

        data = {
            'products':[self.product1.pk, self.product2.pk],
        }
        response = self.client.patch(url, data=data, format='json')

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['products'], [self.product1.id, self.product2.id])


    def test_remove_product_from_wishlist(self):

        self.wishlist.products.add(self.product1, self.product2)
        
        url = reverse('api:wishlist-product-delete-view', kwargs={'pk':self.product1.id})


        response = self.client.put(url)

        # Check the response status code and content
        self.assertEqual(response.status_code, 204)
        self.assertEqual(list(self.wishlist.products.all()), [self.product2])