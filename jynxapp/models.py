from django.db import models
from django.contrib.auth.models import User
import datetime
from django.urls import reverse

# Create your models here.
class UserData(models.Model):
    created_on=models.DateField(auto_now_add=True)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    Username=models.CharField(max_length=220)
    userID=models.CharField(max_length=50)
    phone_num=models.BigIntegerField(default=123)
    profilePic=models.ImageField(upload_to='profilePICS/',default='/default/default_img.png')
    friends=models.ManyToManyField(User,related_name='friend_lists',blank=True)
    friend_requests=models.ManyToManyField(User,related_name='friend_requests',blank=True)
    search_history=models.ManyToManyField(User,related_name='search_history',blank=True)
    viewProfile_permission=models.BooleanField(default=True)
    instagram_handle=models.CharField(max_length=20, default='',blank=True)
    bio=models.TextField(max_length=100,default='',blank=True)

    # settings
    zig_privacy=models.BooleanField(default=False) #True means Private False means public
    reply_notifications=models.BooleanField(default=True)
    friend_requests_notifications=models.BooleanField(default=True)
    email_notifications=models.BooleanField(default=True)
    def __str__(self):
        return f'{self.userID} - {self.user}'
    def get_absolute_url(self):
        return reverse('profile', args=[str(self.id)])


class Zig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='zigs')
    type=models.CharField(max_length=50,default='text_type')
    title = models.TextField(max_length=100)
    public=models.BooleanField(default=True)
    anonymous=models.BooleanField(default=False)
    hidden_replies=models.BooleanField(default=False)
    created_on=models.DateTimeField(auto_now_add=True)
    date=models.DateField()
    image=models.ImageField(upload_to=f'zigImages',default='',blank=True)
    playlist=models.BooleanField(default=False)
    yt_url=models.CharField(default='',max_length=500,blank=True)
    playlist_url=models.CharField(default='',max_length=500,blank=True)
    track_url=models.CharField(default='',max_length=500,blank=True)
    def get_absolute_url(self):
            return reverse('zig', args=[str(self.id)])
    # expiry_date=models.DateTimeField(blank=True)
    def __str__(self):
        return f'{self.user.userdata.userID}:{self.title}'

# Reply is purposely misspelled
class Replie(models.Model):
    card = models.ForeignKey(Zig, on_delete=models.CASCADE,related_name='replies')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    likes=models.ManyToManyField(User,blank=True,related_name='liked_users')
    created_on=models.DateTimeField(auto_now_add=True)
    @property
    def person_username(self):
        return self.sender.userdata.Username
    def __str__(self) :
        return f'{self.card}:{self.sender.userdata.userID}-{self.card.user.userdata.userID}'

class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    category=models.CharField(max_length=100,default='')
    title=models.CharField(max_length=100,default='')
    notification=models.TextField(max_length=220,default='')
    icon=models.ImageField(upload_to='notify_icon',default='',blank=True)
    url=models.CharField(max_length=100,default='',blank=True)
    created_on=models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    zig=models.OneToOneField(Zig,on_delete=models.CASCADE,related_name='zigs',unique=False)
    category=models.CharField(blank=True,max_length=220)
    remark=models.CharField(blank=True,max_length=220)
    
    def __str__(self):
        return f'Category: {self.category} - Title: {self.zig.title}'



    



