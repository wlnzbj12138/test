from django.db import models
from django.contrib.auth.models import User
from django.db.models import Index
from django.utils import timezone  # 新增：用于Profile的时间字段
from django.db.models.signals import post_save  # 新增：信号相关
from django.dispatch import receiver  # 新增：信号相关

# ========== 原有模型：文章 ==========
class Article(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="文章标题",
        db_index=True
    )
    content = models.TextField(verbose_name="文章内容")
    # 移除原有单张封面图字段 cover_image
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name="作者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        indexes = [Index(fields=['-created_at'])]

    def __str__(self):
        return self.title

# ========== 原有模型：文章图片 ==========
class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images', verbose_name="所属文章")
    image = models.ImageField(upload_to='article_images/', verbose_name="文章图片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")

    class Meta:
        verbose_name = "文章图片"
        verbose_name_plural = "文章图片"
        ordering = ['created_at']  # 按上传顺序显示图片

# ========== 原有模型：评论 ==========
class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name="文章")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="评论者")
    content = models.TextField(max_length=500, verbose_name="评论内容")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True, verbose_name="回复的评论")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ['-created_at']

# ========== 原有模型：文章点赞 ==========
class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes', verbose_name="文章")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="点赞用户")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')
        verbose_name = "文章点赞"
        verbose_name_plural = "文章点赞"

# ========== 原有模型：评论点赞 ==========
class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', verbose_name="评论")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="点赞用户")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')
        verbose_name = "评论点赞"
        verbose_name_plural = "评论点赞"

# ========== 新增：用户资料模型（头像+关注功能） ==========
class Profile(models.Model):
    # 一对一关联Django内置User模型（删除用户时同步删除资料）
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="关联用户")
    # 头像上传（存储到media/avatars/目录，允许为空）
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="用户头像")
    # 关注关系（多对多自关联：一个用户可以关注多个用户，也可以被多个用户关注）
    following = models.ManyToManyField(User, related_name='followers', blank=True, verbose_name="关注的人")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

    def __str__(self):
        return f"{self.user.username}的个人资料"

    # 快捷属性：统计关注数
    @property
    def following_count(self):
        return self.following.count()

    # 快捷属性：统计粉丝数
    @property
    def follower_count(self):
        return self.user.followers.count()

# ========== 新增：信号处理（创建User时自动创建Profile） ==========
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建时，自动生成对应的Profile记录"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """用户保存时，同步保存Profile记录"""
    instance.profile.save()