from django.db import models

class Category(models.Model):
    name=models.CharField(max_length=30)
    image=models.ImageField(upload_to="categories")
    description=models.TextField()



class Products(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to="products")
    description = models.TextField()
    price=models.IntegerField()
    stock=models.IntegerField()
    available=models.BooleanField(default=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    categories=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products")

