"""Database Models"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator

def recipe_image_file_path(instance, filename):
    """Generate filepath for new recipe image"""

    # get file extension
    ext = os.path.splitext(filename)[1]

    # create random uuid filename
    filename = f'{uuid.uuid4()}{ext}'

    # return path
    return os.path.join('uploads', 'recipe', filename)

class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex='^(?!.*\.\.)(?!.*\.$)[^\W][\w.]{0,29}$',
                message='Invalid username',
            )
        ]
    )
    fullname = models.CharField(max_length=255, default='Anonim')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    calories = models.DecimalField(max_digits=6, decimal_places=1)
    protein = models.DecimalField(max_digits=6, decimal_places=1)
    carbs = models.DecimalField(max_digits=6, decimal_places=1)
    fibers = models.DecimalField(max_digits=6, decimal_places=1)
    fat = models.DecimalField(max_digits=6, decimal_places=1)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title


class Food(models.Model):
    """Food object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    calories = models.DecimalField(max_digits=6, decimal_places=1)
    carbs = models.DecimalField(max_digits=6, decimal_places=1)
    fibers = models.DecimalField(max_digits=6, decimal_places=1)
    fat = models.DecimalField(max_digits=6, decimal_places=1)
    protein = models.DecimalField(max_digits=6, decimal_places=1)
    estimates = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title
