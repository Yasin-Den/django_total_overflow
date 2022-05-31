from django.db import models
from jsonfield import JSONField


class MyInstaPage(models.Model):
    user_key = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    user_id = models.CharField(max_length=20)
    settings = JSONField()

    def __str__(self):
        return '%s' % self.username


class InstaPK(models.Model):
    insta_pk = models.IntegerField()
    status_tupel = (
        ('pub', 'published'),
        ('drf', 'draft'),
    )
    status = models.CharField(choices=status_tupel, max_length=10)
    page_target = models.ForeignKey(MyInstaPage, on_delete=models.CASCADE)

    def __str__(self):
        return '%s for %s' % (self.insta_pk, self.page_target)


class CommentForUse(models.Model):
    comment = models.CharField(max_length=20)

    def __str__(self):
        return self.comment
