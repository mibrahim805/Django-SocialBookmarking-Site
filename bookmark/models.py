from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField()



class Bookmarks(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    url = models.URLField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.ManyToManyField('Tags', blank=True)
    is_public = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title


class Tags(models.Model):
    name = models.CharField(max_length=200)


    def __str__(self):
        return self.name


class Follow(models.Model):
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('following', 'follower')


