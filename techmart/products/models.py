from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    name =models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    image = models.ImageField(upload_to= 'products/')
    stock = models.PositiveIntegerField(default=10)
    available = models.BooleanField(default=True)
    created_by = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class ProductRating(models.Model):
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        unique_together = ('product', 'user')  # One rating per user

    def __str__(self):
        return f"{self.product.name} - {self.rating} Stars"  


from django.utils.text import slugify

def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.name)
    super().save(*args, **kwargs)
    
    