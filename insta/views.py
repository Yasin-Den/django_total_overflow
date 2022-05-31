import random

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from instagrapi import Client

from .models import MyInstaPage, InstaPK, CommentForUse

from . import tasks as IW


def add_pk_view(request):
    if request.method == 'POST':
        print('----', target_username := request.POST.get('username'), 'for',
              my_username := request.POST.get('page_target'))
        try:
            my_page = get_object_or_404(MyInstaPage, user_key=my_username)
            # IW.get_pk(my_page, target_username)
            IW.GetPk(my_page, target_username).start()
            print('----%s ran:)' % target_username)
            return render(request, 'insta/add_pk.html')
        except:
            return HttpResponse('error in process!')

    return render(request, 'insta/add_pk.html')


def posting_view(request, user_key):
    target_data = random.choice(InstaPK.objects.filter(status='drf', page_target=get_object_or_404(MyInstaPage, user_key=user_key)))
    print(target_data)
    # posting proces
    IW.PostingInInstagram(target_data).start()
    return render(request, 'insta/posting.html', context={'target_data': target_data})


def random_comment_view(request):
    return HttpResponse(random.choice(CommentForUse.objects.all()))


def login_page_view(request, target_user_key):
    page = MyInstaPage.objects.get(user_key=str(target_user_key))
    cl = Client()
    cl.login(page.username, page.password)
    page.settings = cl.get_settings()
    page.save()
    return HttpResponse(cl.get_settings())
