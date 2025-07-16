from django.shortcuts import render,redirect,HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import datetime
from jynxapp import models
from django.http import JsonResponse
from .user_id_generator import generate_unique_userIDS
from django.template import loader
import random



def generate_users(num):
    names=['Rahul','Priyanka','Pratusha','Prachi','Aditya','Jaideep','Raj','Shlok','Mark','helena','Krish','Zera','Alex']
    dp_paths=[r"media/profilePICS/images.jpg",r"media/profilePICS/images.png",r"media/profilePICS/download.png",r"media/profilePICS/Icon ionic-ios-person.png"]
    
    zig_titles=['How am I as a friend','How am I','How do I behave?','What shall I do about my relationship','I have a crush on Aishwarya',"What are y'all thoughts on Rohan?",
                "Am I really annoying?",'Was my new video good?']
    for i in range(num):
        try:
            existing_ids=[]
            for user_instance in models.User.objects.all():
                try:
                    existing_ids.append(user_instance.userdata.userID)
                except Exception as e:
                    print(f'{e}from generator')

            # new user
            user_name=random.choice(names).lower()
            new_user=User.objects.create_user(username=f'{user_name}@gmail.com',email=f'{user_name}@gmail.com',password=user_name)
            new_user.save()

            # user data
            user_id=generate_unique_userIDS(user_name,existing_ids)
            user_data=models.UserData(user=new_user,Username=user_name,phone_num=7903238641,userID=user_id[0],profilePic=random.choice(dp_paths))
            user_data.save()

            # creating zig
            new_zig=models.Zig(user=new_user,title=random.choice(zig_titles))
            new_zig.save()
            # new_user.zig.title(random.choice(zig_titles))

        except Exception as e:
            print(e)
# generate_users(3)