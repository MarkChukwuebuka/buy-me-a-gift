from django.test import TestCase
from .models import *
from django.contrib.auth import get_user_model


# Create your tests here.

User = get_user_model()


class CategoryTests(TestCase):
    
    def test_create_category(self):
        
        cat = Category.objects.create(
            name = 'test_category'                       
        )
        
        self.assertEqual(cat.name, 'test_category')
        


class ProductTest(TestCase):

    def test_create_product(self):

        cat = Category.objects.create(
            name = "test_category"
        )

        product = Product.objects.create(
            name = "test_product",
            price = 50.00,
            rank = 2,
            category = cat,

        )

        self.assertEqual(product.name, 'test_product')
        self.assertEqual(product.price, 50)
        self.assertEqual(product.rank, 2)
        self.assertEqual(product.category, cat)


class ProductTest(TestCase):

    def test_create_wishlist(self):

        user = User.objects.create_user(
            email = 'test@gmail.com',
            password='pass2002word'
        )

        cat1= Category.objects.create(
            name = "test_category"
        )

        cat2= Category.objects.create(
            name = "test_category2"
        )


        product1 = Product.objects.create(
            name = "test_product1",
            price = 5.00,
            rank = 2,
            category = cat1,
        )

        product2 = Product.objects.create(
            name = "test_product2",
            price = 50.00,
            rank = 23,
            category = cat2,
        )

        wishlist = WishList.objects.create(
            user = user,
        )

        wishlist = wishlist.products.add(product1, product2)

        self.assertEqual(wishlist.user.email, 'test@gmail.com')
        self.assertEqual(wishlist.products, [product1, product2])
        # self.assertEqual(product.rank, 2)
        # self.assertEqual(product.category, cat)

