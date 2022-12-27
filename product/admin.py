from django.contrib import admin
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(WishList)

