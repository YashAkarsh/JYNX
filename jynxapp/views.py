from django.shortcuts import render,redirect,HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import datetime
from . import models
from django.http import JsonResponse
from scripts.user_id_generator import generate_unique_userIDS
from django.template import loader
from django.core.paginator import Paginator,EmptyPage
from django.db.models import Prefetch,Q,Case, When,Value,IntegerField
import random
from django.db.models.functions import Now
from django.core.exceptions import *
from django.db.models import Count
from django.template import RequestContext
import os
from PIL import Image,ImageDraw,ImageFont
import textwrap
from django.conf import settings
from django.core.mail import send_mail
import base64,io
from django.core.files.uploadedfile import InMemoryUploadedFile
# Create your views here.
new_user_username=''
new_user_password=''
pwd_reset_code=1

# retrieving data
users=None
#current_page=1

def homepage(request):
    global users

    if request.user.is_anonymous:
        return redirect('landing')
    try:
        request.session['current_page']=1
        all_users = models.User.objects.filter(is_superuser=False).exclude(id=request.user.id)
        try:
            users=all_users.exclude(id__in=request.user.userdata.friends.all())
        except:
            return redirect('login')
        print(len(all_users))
        if len(all_users)>10:
            users=random.sample(list(users),6)
        userProfilePic = request.user.userdata.profilePic
        friend_list = request.user.userdata.friends.all()

        if not request.user.is_anonymous:
            notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')

    
        # other_zigs = models.Zig.objects.filter(public=True).select_related('user__userdata').prefetch_related(
        #         Prefetch('replies', queryset=models.Replie.objects.select_related('sender'))
        #     ).order_by('-created_on')
        
        # friend_zigs = models.Zig.objects.filter(
        #         Q(user__in=friend_list) | Q(user=request.user)
        #     ).select_related('user__userdata').prefetch_related(
        #         Prefetch('replies', queryset=models.Replie.objects.select_related('sender'))
        #     ).order_by('-created_on')

        other_zigs = models.Zig.objects.annotate(
            priority=Case(
                When(Q(user__in=friend_list) | Q(user=request.user), then=Value(1)),
                When(public=True, then=Value(2)),
                default=Value(3),
                output_field=IntegerField()
            )
        ).select_related('user__userdata').prefetch_related(
            Prefetch('replies', queryset=models.Replie.objects.select_related('sender'))
        ).order_by('priority', '-created_on')


        
        items_per_page=3
        pagination = Paginator(other_zigs, items_per_page)
        other_zigs_page = pagination.page(1)
        # replies=models.Replie.objects.filter(card__in=other_zigs_page).order_by('-likes','-created_on')
        other_zigs_lst=[]
        for zig in other_zigs_page.object_list:
            zig_data={
                'zig':zig,
                'replies':models.Replie.objects.filter(card=zig).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
                'user_other_zigs':models.Zig.objects.filter(user=zig.user).exclude(id=zig.id)
            }
            other_zigs_lst.append(zig_data)

    except Exception as e:
        users = models.User.objects.filter(is_superuser=False).exclude(id=request.user.id)
        other_zigs_page = ''
        other_zigs_lst=[]
        userProfilePic=request.user.userdata.profilePic
        notifications=[]
        print(f'{e}|| from homepage function')
        # return redirect('landing')

    if request.method == 'POST':
        form_function = request.POST.get('form_function')

        if form_function=='user_opinion':
            opinion=request.POST.get('opinion')

            if str(opinion)!='':

                zig=request.POST.get('current_zig')
                zig_id=int(zig)
                current_zig=models.Zig.objects.get(id=zig_id)
                add_reply=models.Replie(card=current_zig,sender=request.user,content=opinion)
                add_reply.save()
                if current_zig.user.userdata.reply_notifications==True and current_zig.user!=request.user:
                    notification=models.Notification(user=current_zig.user,category='reply', title='New Reply!',notification=f'You got a new reply',url=f'zig/{zig_id}')
                    notification.save()

                    if current_zig.user.userdata.email_notifications==True:
                        subject = 'You got a new Reply! - JYNX'
                        message = f'Check out the new replies on your zig!'
                        base_url = request.build_absolute_uri('/') if request else settings.BASE_URL

                        full_url = f'{base_url}/zig/{zig_id}'
                        html_message = f'Check out the new replies on your zig!:<br><a href="{full_url}">{full_url}</a>'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [current_zig.user]

                        send_mail(
                            subject,
                            message,
                            email_from,
                            recipient_list,
                            fail_silently=False,
                            html_message=html_message,
                        )

                if add_reply.sender==request.user:
                    response_data={
                        'content':add_reply.content,
                        'reply_id':add_reply.id,
                        'like_count':add_reply.likes.count(),
                        'sender':'You'
                    }
                else:
                    response_data={
                        'content':add_reply.content,
                        'reply_id':add_reply.id,
                        'sender':add_reply.sender.userdata.userID
                    }
            else:
                response_data=''
            return JsonResponse(response_data,safe=False)

        if form_function=='add_friends':
            selected_username=request.POST.get('selected_user')
            selected_user=User.objects.get(id=selected_username)
            selected_user.userdata.friend_requests.add(request.user)
            if selected_user.userdata.friend_requests_notifications== True:
                models.Notification.objects.create(user=selected_user,category='friend_request',notification='You got a friend request!', title='Friend Request!', url='friendlist/')

        if form_function=='search_friends':
            user_query=request.POST.get('src_value')
            matching_users_data=[]
            if user_query!='':
                try:
                    query_search=Q(Q(userID__icontains=user_query) | Q(Username__icontains=user_query))
                    matching_users=models.UserData.objects.filter(query_search)
                    print(matching_users)

                    for matching_user in matching_users:
                        context={
                            'user':matching_user.user
                        }
                        result_html = render(request, 'search_result_content.html', context).content
                        matching_users_data.append(result_html.decode())

                except Exception as e:
                    print(e)
                    print('search failed')

            return JsonResponse(matching_users_data,safe=False)

        if form_function == 'load_zigs':
            #global current_page
            current_page=request.session.get('current_page','default')
            page_index = int(request.POST.get('page'))
            items_per_page = int(request.POST.get('items_per_page'))

            if current_page!=page_index:
                try:
                    other_zigs_list=[]
                    page = pagination.page(page_index)
                    for zig in page.object_list:
                        context = {
                            'zig':zig,
                            'userID':zig.user.userdata.userID,
                            'username':zig.user.userdata.Username,
                            'date':zig.date,
                            'user_all_zigs':models.Zig.objects.filter(user=zig.user).exclude(id=zig.id),
                            'replies': zig.replies.all().annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
                            'title': zig.title,
                            'userPFP':zig.user.userdata.profilePic.url

                            }

                        if zig.image == '':
                            if zig.playlist_url!='' or zig.track_url!='':
                                zig_html = render(request, 'spotifyembed.html', context).content
                            elif zig.yt_url!='':
                                zig_html = render(request, 'youtubeembedzig.html', context).content

                            else:
                                zig_html = render(request, 'previewcard.html', context).content
                        else:

                            zig_html = render(request, 'previewcardImage.html', context).content

                        other_zigs_list.append(zig_html.decode())
                        #current_page=page_index
                        request.session['current_page']=page_index

                except EmptyPage:
                    other_zigs_list = []
                    zig_html = ''
            else:
                print('equal')
                other_zigs_list=[]
                zig_html = ''

            return JsonResponse(other_zigs_list, safe=False)
        if form_function=='deleteZig':
            zig_id=request.POST.get('id')
            found_zig=models.Zig.objects.get(id=zig_id)
            found_zig.delete()
        if form_function=='delete_reply':
            rply_id=request.POST.get('reply_id')
            rply=models.Replie.objects.get(id=rply_id)
            rply.delete()
        if form_function=='search_history':
            user=request.POST.get('user')
            # found_user=models.UserData.objects.get(userID=user).user
            found_user=models.User.objects.get(id=user)
            request.user.userdata.search_history.add(found_user.id)
            request.user.userdata.save()
            print('search_history updated')

        if form_function=='delete_history':
            user=request.POST.get('user')
            found_user=models.User.objects.get(id=user)
            request.user.userdata.search_history.remove(found_user.id)
            request.user.userdata.save()


        if form_function=='delete_notifications':
            user_notifications=models.Notification.objects.filter(user=request.user)
            user_notifications.delete()
            print('notifications deleted')

        if form_function=='liked':
            status=''
            print('liked')
            reply_id=request.POST.get('reply_id')
            reply=models.Replie.objects.get(id=reply_id)

            if request.user in reply.likes.all():
                reply.likes.remove(request.user)
                status='disliked'
            else:
                reply.likes.add(request.user)
                status='liked'


            return HttpResponse(status)

        if form_function=='report':
            category=request.POST.get('category')
            if category=='zig':
                id=request.POST.get('zig')
                zig=models.Zig.objects.get(id=id)
                try:
                    models.Report.objects.get(zig=zig)

                except:
                    new_report=models.Report(zig=zig,category=category)
                    new_report.save()
            elif category=='reply':
                id=request.POST.get('reply')
                reply=models.Replie.objects.get(id=id)
                print(reply)
                try:
                    models.Report.objects.get(zig=reply.card)

                except:
                    new_report=models.Report(zig=reply.card,category=category)
                    new_report.save()

    context = {
        'zigs': other_zigs_lst,
        # 'replies':replies,
        # 'top_replies':top_replies,
        'users': users,
        'profile_pic_url': userProfilePic.url,
        'notifications':notifications
    }
    return render(request, 'index.html', context)

def loginUser(request):
    if not request.user.is_anonymous:
        return redirect('homepage')
    if request.method=='POST':
        email=request.POST.get('email').lower()
        password=request.POST.get('password')
        user=authenticate(username=email,email=email,password=password)
        if user is not None:
            login(request,user)
            print(f'User authenticated: {datetime.datetime.now().strftime("%H:%M")} {request.user}')
            return redirect('homepage')
        else:
            print('invalid credentials')
            return render(request,'login.html',context={'validity':False})


    return render(request,'login.html', context={'validity':True})

def signupUser(request):
    # global new_user_password
    # global new_user_username,otp
    if request.method=='POST':
        email=request.POST.get('email').lower().strip()
        password=request.POST.get('password').strip()

        if models.User.objects.filter(username__iexact=email).exists():
            return redirect('login')

        otp=random.randint(1000,9999)
        request.session['otp']=otp
        print(f'otp:{otp}')
        subject = 'Email Verification - JYNX'
        message = f'Here is your OTP for verification:- {otp}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]

        send_mail( subject, message, email_from, recipient_list )
        # new_user=User.objects.create_user(username=f'{datetime.datetime.now().strftime("%H:%M")} unknown',email=email,password=password)
        new_user_username=email
        new_user_password=password

        request.session['new_user_username']=email
        request.session['new_user_password']=password

        return redirect('email_confirmation')

        # return redirect('profile_creation')
    return render(request,'signUp.html')

def logoutUser(request):

    print(f'Logged Out User: {datetime.datetime.now().strftime("%H:%M")} {request.user}')
    logout(request)
    return redirect('homepage')

def profile_create(request):
    # global new_user_username
    # global new_user_password
    new_user_username=request.session.get('new_user_username','default')
    new_user_password=request.session.get('new_user_password','default')

    if not request.user.is_anonymous:
        return redirect('homepage')
        # pass
    existing_userIDs=[]
    for user_instance in models.User.objects.prefetch_related('userdata'):
        try:
            existing_userIDs.append(user_instance.userdata.userID)
        except Exception as e:
            print(e,f'user: {user_instance}')
    
    if request.method=='POST':
        username=request.POST.get('username')
        # phone_num=request.POST.get('phone_num')
        user_id=request.POST.get('userID').strip()
        user_id=user_id.replace(' ','')
        try:
            profile_pic=request.FILES['profilePic']
        except:
            profile_pic=''

        bio=request.POST.get('bio')
        if user_id not in existing_userIDs:
            # creating new user

            new_user=User.objects.create_user(username=new_user_username,email=new_user_username,password=new_user_password)
            new_user.save()
            print(f'NEW USER CREATED, Username: {new_user_username} Password:{new_user_password}')

            # authenticating
            user=authenticate(username=new_user_username,email=new_user_username,password=new_user_password)
            if user is not None:
                login(request,user)
                print(f'User authenticated: {datetime.datetime.now().strftime("%H:%M")} {request.user}')

                try:
                    # adding user data
                    if profile_pic!='':
                        try:
                            i = Image.open(profile_pic)
                            thumb_io = io.BytesIO()
                            i.save(thumb_io, format='JPEG', quality=50)
                            inmemory_uploaded_file = InMemoryUploadedFile(thumb_io, None, f'{user_id}.jpeg',
                                                                    'image/jpeg', thumb_io.tell(), None)
                        except:
                            inmemory_uploaded_file=profile_pic
                        user_data=models.UserData(user=request.user,Username=username,bio=bio,userID=user_id,profilePic=inmemory_uploaded_file)
                    else:
                        user_data=models.UserData(user=request.user,Username=username,bio=bio,userID=user_id)
                    user_data.save()
                except:
                    request.user.delete()
            else:
                print('invalid credentials')
        else:
            print('User id already exists')
            return HttpResponse('user_id_exists')
        id_suggestion=generate_unique_userIDS(username,existing_userIDs)
        print(id_suggestion)
        context={
            'suggestions':id_suggestion
        }
    else:
        context={
            'suggestion':'',
        }
    return render(request,'createprofile.html',context)


def profilepage(request,user_query):
    found=True
    userFound=None
    friends_num=None
    friend_requests_num=None
    user_zigs=None
    replies=None
    notifications=''


    try:
        userFound=models.UserData.objects.get(userID=user_query).user
        found=True
    except:
        found=False

    if found==True:
        if not request.user.is_anonymous:
            notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')

        user_zigs=models.Zig.objects.filter(user=userFound).order_by('-created_on')
        # user_zigs=user_zigs.filter(public=True)
        replies=models.Replie.objects.filter(card__in=user_zigs).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on')
        friends_num=userFound.userdata.friends.all().count()
        friend_requests_num=userFound.userdata.friend_requests.count()
        context={
                'user':userFound,
                'friends_num':friends_num,
                'friend_requests_num':friend_requests_num,
                'user_zigs':user_zigs,
                'my_zig_replies':replies,
                'notifications':notifications
            }

    else:
        return render(request,'404.html')

    return render(request, 'viewprofile.html',context)
def settings_ProfilePage(request):
    if request.user.is_anonymous:
        return redirect('landing')
    notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')

    if request.method=='POST':
        form_function=request.POST.get('form_function')

        if form_function=='change_pf_data':
            new_username=request.POST.get('username')
            new_phone_num=request.POST.get('phone_num')
            new_email=request.POST.get('email')
            new_user_id=request.POST.get('user_id')
            new_user_id=request.POST.get('user_id').strip()
            new_user_id=new_user_id.replace(' ','')
            new_pfView=request.POST.get('pfView')
            new_ig_id=request.POST.get('ig_id')
            new_bio=request.POST.get('bio')
            try:
                profile_pic=request.FILES['profilePic']
            except:
                profile_pic=None

            if profile_pic!=None:
                try:
                    i = Image.open(profile_pic)
                    thumb_io = io.BytesIO()
                    i.save(thumb_io, format='JPEG', quality=50)
                    inmemory_uploaded_file = InMemoryUploadedFile(thumb_io, None, f'{request.user.userdata.userID}.jpeg',
                                                            'image/jpeg', thumb_io.tell(), None)
                except:
                    print('ERROR COMPRESSING FILE')
                    inmemory_uploaded_file=profile_pic
                request.user.userdata.profilePic=inmemory_uploaded_file
                request.user.userdata.save()

            current_user=request.user.userdata
            if new_username!='':
                current_user.Username=new_username.strip()

            try:
                current_user.phone_num=new_phone_num
            except:
                pass

            if not models.UserData.objects.filter(userID__iexact=new_user_id).exists() and new_user_id!='':
                current_user.userID=new_user_id.strip()
            current_user.instagram_handle=new_ig_id.strip()
            current_user.bio=new_bio.strip()
            if new_pfView=='true':
                current_user.viewProfile_permission=True
            else:
                current_user.viewProfile_permission=False
            if new_email!='':
                request.user.email=new_email
            request.user.save()
            request.user.userdata.save()

    return render(request, 'settings.profile.html',context={'notifications':notifications})

def settings_MyZigPage(request):
    if request.user.is_anonymous:
        return redirect('landing')
    notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')
    if request.method=='POST':
        form_function=request.POST.get('form_function')
        if form_function=='change_zigSettings':
            private_zigs=request.POST.get('private_zigs')


            # updating new data

            current_user=request.user.userdata
            if private_zigs=='true':
                current_user.zig_privacy=True
            else:
                current_user.zig_privacy=False

            request.user.userdata.save()

    return render(request, 'settings.myzigs.html',context={'notifications':notifications})
def settings_NotificationsPage(request):
    if request.user.is_anonymous:
        return redirect('landing')
    notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')

    if request.method=='POST':
        reply_notifications=request.POST.get('reply_notifications')
        friend_requests_notifications=request.POST.get('friend_requests_notifications')
        email_notifications=request.POST.get('email_notifications')
        if reply_notifications=='true':
            request.user.userdata.reply_notifications=True
        else:
            request.user.userdata.reply_notifications=False

        if friend_requests_notifications=='true':
            request.user.userdata.friend_requests_notifications=True
        else:
            request.user.userdata.friend_requests_notifications=False

        if email_notifications=='true':
            request.user.userdata.email_notifications=True
        else:
            request.user.userdata.email_notifications=False
        request.user.userdata.save()

    return render(request, 'settings.notifications.html',context={'notifications':notifications})

def zig(request, id):
    try:
        zig=models.Zig.objects.get(id=id)
        context={'zig':zig,
            'replies':models.Replie.objects.filter(card=zig).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
            'user_all_zigs':models.Zig.objects.filter(user=zig.user).exclude(id=zig.id),
            }

    except ObjectDoesNotExist as e:
        print(e)
        return render(request,'404.html')

    return render(request,'zig.html',context)

def createzig(request):
    if request.user.is_anonymous:
        return redirect('landing')
    notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')

    if request.method=='POST':
        anonymous=False
        mode=None
        playlist=False

        title=request.POST.get('title','')
        identity=request.POST.get('identity')
        zig_mode=request.POST.get('zig_mode')
        hide_replies=request.POST.get('hide_replies')
        zig_type=request.POST.get('zig_type')
        yt_url=request.POST.get('yt_url')
        track_url=request.POST.get('track_url')
        playlist_url=request.POST.get('playlist_url')


        if zig_type=='0':
            zig_type='text_type'
        elif zig_type=='1':
            zig_type='yt_type'
        elif zig_type=='2':
            zig_type='song_type'


        if len(yt_url)!=0:
            yt_url=yt_url.removeprefix('https://youtu.be/')
            yt_url=yt_url.split('?')[0]
        if len(track_url)!=0:
            track_url=track_url.removeprefix('https://open.spotify.com/track/')
            track_url=track_url.split('?')[0]

        if len(playlist_url)!=0:
            playlist=True

            playlist_url=playlist_url.removeprefix('https://open.spotify.com/')

            playlist_url=playlist_url.split('?')[0]

            print(playlist_url)

        try:
            zig_image=request.FILES['zig_image']
        except:
            zig_image=None

        if identity=='true':
            anonymous=True

        if zig_mode=='Public':
            mode=True
        else:
            mode=False

        if hide_replies=='true':
            hide_replies=True
        else:
            hide_replies=False
        new_zig=models.Zig(user=request.user,title=title,date=datetime.date.today(),image=zig_image,anonymous=anonymous,public=mode,hidden_replies=hide_replies,type=zig_type,yt_url=yt_url,playlist_url=playlist_url,track_url=track_url,playlist=playlist)
        new_zig.save()
        print('creating new zig')
        print('Status:-')
        print(f'Anonymous- {identity}')
        print(f'Public- {mode}')
        print(f'Hidden Replies- {hide_replies}')
    return render(request, 'createzigs.html',context={'notifications':notifications})

def friendlist(request):
    if request.user.is_anonymous:
        return redirect('landing')
    notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')

    if request.method=='POST':
        action=request.POST.get('action')
        selected_user=request.POST.get('highlighted_user')
        selected_user=User.objects.get(id=selected_user)
        if action=='accept':
            request.user.userdata.friends.add(selected_user)
            selected_user.userdata.friends.add(request.user)
            request.user.userdata.friend_requests.remove(selected_user)
            if selected_user.userdata.friend_requests_notifications==True:
                models.Notification.objects.create(user=selected_user,category='friend_request',notification=f'{request.user.userdata.userID} accepted your friend request!', title='Accepted Friend Request', url='friendlist/')
        elif action=='reject':
            request.user.userdata.friend_requests.remove(selected_user)

        elif action=='unfriend':
            request.user.userdata.friends.remove(selected_user)
            selected_user.userdata.friends.remove(request.user)


    return render(request, 'friendlist.html',context={'notifications':notifications})



def discover(request):
    if request.user.is_anonymous:
        return redirect('landing')
    notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')

    profile_zig_1={}
    profile_zig_2={}
    mid_zigs_1=[]
    mid_zigs_2=[]
    AllPublic_users=models.User.objects.all()
    AllPublic_users=AllPublic_users.exclude(id=request.user.id)
    # AllPublic_users=AllPublic_users.exclude(viewProfile_permission=False)
    AllPublic_users=AllPublic_users.filter(is_superuser=False,userdata__viewProfile_permission=True)
    print(AllPublic_users)
    for i in AllPublic_users:
        zig_objs=models.Zig.objects.filter(user=i,public=True,anonymous=False)
        if not zig_objs.exists():

            AllPublic_users= AllPublic_users.exclude(id=i.id)
            # public_users_lst=random.sample(AllPublic_users,2)
    AllPublic_users= list(AllPublic_users)
    public_users_lst=random.sample(AllPublic_users,2)

    profile_zig_1={
        'user':public_users_lst[0],
        'zigs':models.Zig.objects.filter(user=public_users_lst[0],anonymous=False,public=True)[:4],
    }
    profile_zig_2={
        'user':public_users_lst[1],
        'zigs':models.Zig.objects.filter(user=public_users_lst[1],anonymous=False,public=True)[:4],
    }

    # AllPublic_zigs=models.Zig.objects.exclude(user__in=request.user.userdata.friends.all())
    AllPublic_zigs=models.Zig.objects.filter(user__in=AllPublic_users)

    AllPublic_zigs=AllPublic_zigs.exclude(user=request.user.id)
    AllPublic_zigs=list(AllPublic_zigs.filter(public=True))

    public_zig_lst=random.sample(AllPublic_zigs,2)
    mid_zigs_1=[
        {
            'zig':public_zig_lst[0],
            'replies':models.Replie.objects.filter(card=public_zig_lst[0]).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
            'user_other_zigs':models.Zig.objects.filter(user=public_zig_lst[0].user).exclude(id=public_zig_lst[0].id)

        },
        {
            'zig':public_zig_lst[1],
            'replies':models.Replie.objects.filter(card=public_zig_lst[1]).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
            'user_other_zigs':models.Zig.objects.filter(user=public_zig_lst[1].user).exclude(id=public_zig_lst[1].id)

        }
    ]
    public_zig_lst=random.sample(AllPublic_zigs,2)
    mid_zigs_2=[
        {
            'zig':public_zig_lst[0],
            'replies':models.Replie.objects.filter(card=public_zig_lst[0]).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
            'user_other_zigs':models.Zig.objects.filter(user=public_zig_lst[0].user).exclude(id=public_zig_lst[0].id)

        },
        {
            'zig':public_zig_lst[1],
            'replies':models.Replie.objects.filter(card=public_zig_lst[1]).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
            'user_other_zigs':models.Zig.objects.filter(user=public_zig_lst[1].user).exclude(id=public_zig_lst[1].id)

        }
    ]

    for i in mid_zigs_1:
        if i in mid_zigs_2:
            mid_zigs_1.remove(i)
            public_zig_lst=random.sample(AllPublic_zigs,1)
            mid_zigs_1.append(public_zig_lst)

    if request.method=='POST':
        public_users_lst=random.sample(AllPublic_users,2)
        for i in public_users_lst:
            zig_objs=models.Zig.objects.filter(user=i,public=True,anonymous=False)
            if len(zig_objs)==0:
                AllPublic_users.remove(i)
                public_users_lst=random.sample(AllPublic_users,2)

        profile_zig_1={
            'user':public_users_lst[0],
            'zigs':models.Zig.objects.filter(user=public_users_lst[0],public=True,anonymous=False)[:4],
        }
        profile_zig_2={
            'user':public_users_lst[1],
            'zigs':models.Zig.objects.filter(user=public_users_lst[1],public=True,anonymous=False)[:4],
        }

        public_zig_lst=random.sample(AllPublic_zigs,2)
        mid_zigs_1=[
            {
                'zig':public_zig_lst[0],
                'replies':models.Replie.objects.filter(card=public_zig_lst[0]).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
                'user_other_zigs':models.Zig.objects.filter(user=public_zig_lst[0].user).exclude(id=public_zig_lst[0].id)

            },
            {
                'zig':public_zig_lst[1],
                'replies':models.Replie.objects.filter(card=public_zig_lst[1]).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
                'user_other_zigs':models.Zig.objects.filter(user=public_zig_lst[1].user).exclude(id=public_zig_lst[1].id)

            }
        ]
        public_zig_lst=random.sample(AllPublic_zigs,2)
        mid_zigs_2=[
            {
                'zig':public_zig_lst[0],
                'replies':models.Replie.objects.filter(card=public_zig_lst[0]).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
                'user_other_zigs':models.Zig.objects.filter(user=public_zig_lst[0].user).exclude(id=public_zig_lst[0].id)

            },
            {
                'zig':public_zig_lst[1],
                'replies':models.Replie.objects.filter(card=public_zig_lst[1]).annotate(likes_count=Count('likes')).order_by('-likes_count','-created_on'),
                'user_other_zigs':models.Zig.objects.filter(user=public_zig_lst[1].user).exclude(id=public_zig_lst[1].id)

            }
        ]

        for i in mid_zigs_1:
            if i in mid_zigs_2:
                mid_zigs_1.remove(i)
                public_zig_lst=random.sample(AllPublic_zigs,1)
                mid_zigs_1.append(public_zig_lst)

        context={
        'user_1':profile_zig_1,
        'user_2':profile_zig_2,
        'mid_zig_1':mid_zigs_1,
        'mid_zig_2':mid_zigs_2,
        }

        discover_html = render(request, 'discover_content.html', context).content
        return JsonResponse(discover_html.decode(),safe=False)
    context={
        'user_1':profile_zig_1,
        'user_2':profile_zig_2,
        'mid_zig_1':mid_zigs_1,
        'mid_zig_2':mid_zigs_2,
        'notifications':notifications

    }

    return render(request, 'discover.html',context=context)

def landing(request):
    if not request.user.is_anonymous:
        return redirect('/')
    return render(request, 'landing.html')

def meetdevs(request):
    if not request.user.is_anonymous:
        notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')
    else:
        notifications=''
    return render(request, 'meetthedevelopers.html',context={'notifications':notifications})
def help(request):
    if request.user.is_anonymous:
        return redirect('landing')
    return render(request, 'settings.help.html')

def settings_Account(request):
    if request.user.is_anonymous:
        return redirect('landing')
    if request.method=='POST':
        form_function=request.POST.get('form_function')
        if form_function=='reset_pwd':
            current_pwd=request.POST.get('current_pwd')
            new_pwd=request.POST.get('new_pwd')

            if not request.user.check_password(current_pwd):
                return HttpResponse('not same')

            else:
                request.user.set_password(new_pwd)
                request.user.save()
        elif form_function=='delete_account':

            request.user.delete()

    return render(request, 'settings.accountcontrol.html')
def share(request):
    if request.method=='POST':
        form_function=request.POST.get('form_function')
        if form_function=='shareImage':
            zig_id=request.POST.get('zig')
            zig=models.Zig.objects.get(id=zig_id)
            title=zig.title
            if zig.hidden_replies==True:
                comments=models.Replie.objects.filter(card=zig,sender=request.user).values_list('content', flat=True).annotate(likes_count=Count('likes')).order_by('-likes_count')[:10]
            else:
                comments=models.Replie.objects.filter(card=zig).values_list('content', flat=True).annotate(likes_count=Count('likes')).order_by('-likes_count')[:10]

            try:

                    template=random.choice(['navy_blue.png','orange.png','dark_green.png'])
                    image_path = os.path.join(settings.BASE_DIR, 'static/image', template)
                    img=Image.open(image_path)
                    image=ImageDraw.Draw(img)


                    X=img.width
                    Y=200

                    font_size=65

                    title_font = ImageFont.truetype(os.path.join(settings.BASE_DIR, 'static/fonts', 'title_font.ttf'),font_size)

                    title_default=title.split(' ')

                    if len(title_default)<=10:
                        print(len(title_default),'len')
                        wrapper=textwrap.TextWrapper(width=30)
                        title_default=" ".join(title_default)

                        font_size=65

                    elif len(title_default)>10:

                        print(len(title_default),'len')
                        wrapper=textwrap.TextWrapper(width=45)
                        font_size=45
                        Y=180
                        title_default=title_default[:23]
                        title_default=" ".join(title_default)
                        title_default=title_default+'...'
                        print(title_default)

                            # title_default=title_default.replace(title_default[200:],'...')
                    # title_default=" ".join(title_default)
                    title_font = ImageFont.truetype(os.path.join(settings.BASE_DIR, 'static/fonts', 'title_font.ttf'),font_size)

                    title=wrapper.fill(text=title_default)

                    bbox = image.textbbox((0, 0), title, font=title_font)

                    text_width = bbox[2] - bbox[0]
                    if zig.anonymous!=True:
                        userid="~"+zig.user.userdata.userID
                    else:
                        userid='~Anonymous'

                    userid_width=image.textlength(userid)
                    image.text(((X-userid_width-100)/2,Y-50),userid,font=ImageFont.truetype(os.path.join(settings.BASE_DIR, 'static/fonts', 'comments_font.ttf'),30),fill=(255,255,255) )
                    image.multiline_text(((X-text_width)/2,Y), title, font=title_font ,fill=(255,255,255))


                    # comment section
                    icon=Image.open(os.path.join(settings.BASE_DIR, 'static/image', 'anonym_icon.jpeg'))
                    icon=icon.resize((70,70))
                    # comments=['Noice','Bohot kharaab','hello dear how are you????hello dear how are you????hello dear how are you????hello dear how are you????hello dear how are you????hello dear how are you????','gud gud''Noice','Bohot kharaab','hello dear how are you????','gud gud']

                    image.text(((X-600)/2,600), 'Anonymous Comments', font=ImageFont.truetype(os.path.join(settings.BASE_DIR, 'static/fonts', 'comments_font.ttf'),50) ,fill=(0,0,0))


                    cmt_y=750
                    cmt_font_size=45

                    for comment in comments:
                        wrapper_2=textwrap.TextWrapper(width=40)
                        comment=wrapper_2.fill(text=comment.strip())

                        bbox_2 = image.textbbox((0, 0), comment, font=ImageFont.truetype(os.path.join(settings.BASE_DIR, 'static/fonts', 'comments_font.ttf'),cmt_font_size))
                        cmt_width = bbox_2[2] - bbox_2[0]
                        cmt_height=bbox_2[3]-bbox_2[1]

                        Image.Image.paste(img,icon,(20,cmt_y-10))
                        # image.multiline_text((150,cmt_y), comment, font=ImageFont.truetype(os.path.join(settings.BASE_DIR, 'static/fonts', 'comments_font.ttf'),cmt_font_size) ,fill=(0,0,0))
                        image.multiline_text((150,cmt_y), comment,  font=ImageFont.truetype(os.path.join(settings.BASE_DIR, 'static/fonts', 'comments_font.ttf'),cmt_font_size) ,fill=(0,0,0))
                        # if cmt_y>1428:
                        #     break
                        cmt_y+=cmt_height+50
                    # img.show()
                # with open(image_path, 'rb') as f:
                #     image_data = f.read()

                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG')
                    base64_image = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
                    return JsonResponse({'image': str(base64_image)})
                    # return HttpResponse('namaste')

            except FileNotFoundError:
                return HttpResponse('error finding the file')
    return render(request, 'share.html')


def email_confirmation(request):
    # global otp\
    otp=request.session.get('otp','default')
    validity=True
    if request.method=='POST':
        num1=request.POST.get('ist')
        num2=request.POST.get('sec')
        num3=request.POST.get('third')
        num4=request.POST.get('fourth')
        user_inp=num1+num2+num3+num4

        print(otp)
        if not user_inp.isnumeric():
            validity=False
            return render(request,'email_confirmation.html',context={'validity':validity})

        if otp==int(user_inp):
            return redirect('profile_creation')
        else:
            validity=False
            return render(request,'email_confirmation.html',context={'validity':validity})

    return render(request,'email_confirmation.html',context={'validity':validity})

def about(request):
    if not request.user.is_anonymous:
        notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')
    else:
        notifications=''
    return render(request, 'about.html',context={'notifications':notifications})
def tandc(request):
    if not request.user.is_anonymous:
        notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')
    else:
        notifications=''
    return render(request, 'tandc.html',context={'notifications':notifications})
def privacy(request):
    if not request.user.is_anonymous:
        notifications=models.Notification.objects.filter(user=request.user).order_by('-created_on')
    else:
        notifications=''
    return render(request, 'privacy.html',context={'notifications':notifications})

def passreset(request):
    global pwd_reset_code
    if request.method=='POST':
        email=request.POST.get('email').lower()
        chars='abcdefghijklmnopqrstuvwxyz'

        nums='0123456789'
        reset_code=random.sample(list(chars),8)+random.sample(list(nums),5)
        reset_code=''.join(reset_code)
        pwd_reset_code=reset_code
        subject = 'Forgot Password - JYNX'
        base_url = request.build_absolute_uri('/') if request else settings.BASE_URL
        full_url = f'{base_url}reset_pass/{reset_code}/{email}'
        message = f"Click on this link to reset your password - {full_url}"


        recipient_list = [email]


        email_from = settings.EMAIL_HOST_USER

        send_mail( subject, message, email_from, recipient_list )
        return render(request,'pwd_reset_done.html')
    return render(request, 'password_reset.html')

def reset_pass_code(request,code,email):
    global pwd_reset_code
    if code==pwd_reset_code:
        if request.method=='POST':
            new_pwd=request.POST.get('new_password').strip()
            confirm_pwd=request.POST.get('confirm_password').strip()

            if new_pwd==confirm_pwd:
                if models.User.objects.filter(username=email).exists():
                    query_user=models.User.objects.get(username=email)
                    query_user.set_password(new_pwd)
                    query_user.save()
                    return redirect('login')
            else:
                return render(request,'password_reset_form.html', context={'successful':False})


        return render(request,'password_reset_form.html',context={'successful':True,'email':email,'code':code})
    else:
        return render(request,'404.html')
def contact(request):
    if request.method=='POST':
        print('ij')
        subject = 'User-Review'
        message = f"From-{request.POST.get('user_email')}\nReview:-\n" + request.POST.get('user_message')
        email_from = settings.EMAIL_HOST_USER
        recipient = ['jynx8431@gmail.com']

        send_mail( subject, message, email_from, recipient )


    return render(request, 'contact.html')
