from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from ckeditor.fields import RichTextField


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=150)
    content = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/')
    date_posted = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    saves = models.ManyToManyField(User, related_name="saved_posts", blank=True)

    def total_likes(self):
        return self.likes.count()

    def total_saves(self):
        return self.saves.count()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('view_posts', kwargs={"pk": self.pk})
    
class Comment(models.Model):
    post = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    flagged_for_cyberbullying = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    warnings = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username