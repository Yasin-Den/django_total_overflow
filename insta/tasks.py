from instagrapi import Client
import urllib.request

import time
import random
import os

from django.conf import settings
from instagrapi.exceptions import UnknownError

from .models import CommentForUse, InstaPK

import threading


class InstaPosting:
    def __init__(self, target_data):
        self.pk = target_data.insta_pk
        self.my_page = target_data.page_target
        self.cl = Client(settings=self.my_page.settings)
        self.video_path = os.path.join(settings.MEDIA_ROOT, 'insta_videos_downloaded', f"{self.pk}.mp4")
        self.thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'insta_videos_downloaded', f"{self.pk}.mp4.jpg")
        self.clip = None
        self.caption = ''

    def __str__(self):
        return 'posting %s in page (%s) with caption: \n[[%s]]' % (self.pk, self.my_page.username, self.caption,)

    def download_video(self):
        self.clip = self.cl.media_info(media_pk=int(self.pk))
        time.sleep(5)
        try:
            url_link = self.clip.video_url
            print("---- url :", url_link)
            # print("---- path of video :", self.video_path)
            urllib.request.urlretrieve(url_link, self.video_path)
            self.caption = self.clip.caption_text
        except:
            pass
        return self.clip

    def new_caption(self):
        text = self.caption
        new_user = "@%s" % self.my_page.username

        y = text.split("@")
        # print (y)
        capt = []
        self.caption = ""
        for i in y:
            if y.index(i) == 0:
                for aray in i.split(" "):
                    # print(aray)
                    capt.append(aray)
            if not (y.index(i) == 0):
                # print("ok")
                z = i.split(" ")
                # print(z)
                z.remove(z[0])
                # print(z)
                z.insert(0, new_user)
                if "" in z:
                    z.remove("")
                # print(z)
                capt += z
        # print(capt)
        for i in capt:
            self.caption += i + " "
        return self.caption

    def upload_video(self, reels: bool = False):
        self.cl.login_flow()
        if reels:
            self.clip = self.cl.clip_upload(path=self.video_path, caption=str(self.caption))
            print('---- uploaded reels (%s) in page (%s) successfully' % (self.clip.pk, self.my_page.username))
        else:
            try:
                self.clip = self.cl.video_upload(path=self.video_path, caption=str(self.caption))
                print('---- uploaded post (%s) in page (%s) successfully' % (self.clip.pk, self.my_page.username))
            except UnknownError:
                self.video_path = os.path.join(settings.MEDIA_ROOT, 'insta_videos_downloaded', f"{self.pk}.mp4")
                self.thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'insta_videos_downloaded', f"{self.pk}.mp4.jpg")
                self.clip = self.cl.clip_upload(path=self.video_path, caption=str(self.caption))
                print('---- uploaded reels (%s) in page (%s) successfully' % (self.clip.pk, self.my_page.username))
        return self.clip

    def comment_post(self):
        time.sleep(30)
        if not ("#" in self.caption):
            if self.my_page.username == "mood.overflow":
                hashtags = "#lofi #lofihiphop #lofiedits #lofibeats #lofimusic #lofifilter #newmusicalert #synthwave #vapourwave #vaporwaveaesthetic #vaporwaveart #vaporwavedits #vaporwave #mood #chillin #chilledits #chillmusic #chillbeats #chillvibes #animeedits #amvedits #skateboardedits #beatmaker #animeaesthetic #anime #retro #aesthetic #tumblr #lofibeats"
            elif self.my_page.username == "@dance.overflow":
                hashtags = "#dance #dancer #dancing #dancers #doouyin #douyinchina #ullzang #uzzlangstyle #china #chinesedance #tomame #dancecover #kpop #kstyle #koreandance"
            else:
                hashtags = "#engineering #mechanical #science #technology #engthings #industrial #industry #industrial_tech #usa #canada #new #amazing #gigizmos #giinovations #engineeringtube #engineeringgadgets"
            # print(hashtags)
            self.cl.media_comment(media_id=str(self.clip.id), text=hashtags)
            print('---- commented #')
        else:
            print('---- no need for #')
        target_comment = random.choice(CommentForUse.objects.all()).comment
        self.cl.media_comment(media_id=str(self.clip.id), text=target_comment)
        print('---- commented (%s)' % target_comment)


def get_pk(my_page, target_username):
    all_pk = InstaPK.objects.values_list('insta_pk')

    cl = Client(settings=my_page.settings)
    cl.login_flow()
    time.sleep(3)
    target_user_id = cl.user_id_from_username(target_username)
    print('---- target user id:', target_user_id)
    time.sleep(2)
    media_amount = cl.user_info(user_id=target_user_id).media_count
    print('---- media amount of target:', media_amount)
    time.sleep(3)
    all_media = cl.user_medias(user_id=target_user_id, amount=media_amount)
    for i in all_media:
        if i.media_type == 2 and not ((i.pk,) in all_pk):
            InstaPK.objects.create(insta_pk=i.pk, status='drf', page_target=my_page)
            print('---- %s saved in data base:)' % i.pk)
    else:
        print('---- finished:)')


class PostingInInstagram(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        insta_posting = InstaPosting(self.data)
        try:
            downloading_data = insta_posting.download_video().dict()
            insta_posting.new_caption()
            uploading_data = insta_posting.upload_video()
            # edit data-base
            self.data.status = 'pub'
            self.data.save()
        except UnknownError:
            pass
        # remove video and thumbnail file
        os.remove(insta_posting.video_path)
        os.remove(insta_posting.thumbnail_path)
        # commenting post
        insta_posting.comment_post()
        print('---- finished:)')


class GetPk(threading.Thread):
    def __init__(self, my_page, target_username):
        self.my_page = my_page
        self.target_username = target_username
        threading.Thread.__init__(self)

    def run(self):
        all_pk = InstaPK.objects.values_list('insta_pk')

        cl = Client(settings=self.my_page.settings)
        cl.login_flow()
        time.sleep(3)
        target_user_id = cl.user_id_from_username(self.target_username)
        print('---- target user id:', target_user_id)
        time.sleep(2)
        media_amount = cl.user_info(user_id=target_user_id).media_count
        print('---- media amount of target:', media_amount)
        time.sleep(3)
        all_media = cl.user_medias(user_id=target_user_id, amount=media_amount)
        for i in all_media:
            if i.media_type == 2 and not ((i.pk,) in all_pk):
                InstaPK.objects.create(insta_pk=i.pk, status='drf', page_target=my_page)
                print('---- %s saved in data base:)' % i.pk)
        else:
            print('---- finished:)')
