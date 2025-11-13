from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import PasswordInput


class SignupForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','password1','password2','email','first_name','last_name']
class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=PasswordInput)
from shop.models import Category, Products
class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields="__all__"
class ProductForm(forms.ModelForm):
    class Meta:
        model=Products
        fields=['name','description','price','stock','categories','image']
class StockForm(forms.ModelForm):
    class Meta:
        model=Products
        fields=['stock']