from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.db.models import Count, Prefetch
from django.core.exceptions import SuspiciousFileOperation
from .models import Article, Comment, Like, CommentLike, ArticleImage, Profile
from .forms import ArticleForm, CommentForm, ReplyForm
from django.contrib.auth.models import User

# 新增：全局打印调试装饰器（可选，方便看日志）
def debug_print(func):
    def wrapper(request, *args, **kwargs):
        print(f"\n===== 访问 {func.__name__} 视图 =====")
        if request.method == 'POST':
            print(f"POST数据: {request.POST}")
            if 'images' in request.FILES:
                print(f"文件数量: {len(request.FILES.getlist('images'))}")
        return func(request, *args, **kwargs)
    return wrapper


# ========== 原有视图：文章创建（保留所有逻辑） ==========
@login_required
@debug_print
def article_create(request):
    if request.method == 'POST':
        article_form = ArticleForm(request.POST)

        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.author = request.user
            article.save()

            images = request.FILES.getlist('images')
            print(f"📸 接收到的图片数量: {len(images)}")

            if len(images) > 4:
                article.delete()
                return render(request, 'blog/article_create.html', {
                    'article_form': article_form,
                    'error': '⚠️ 最多只能上传4张图片！'
                })

            error_msg = ""
            for idx, img in enumerate(images, 1):
                try:
                    if not img.content_type.startswith('image/'):
                        error_msg = f"⚠️ 第{idx}个文件不是图片格式！"
                        continue
                    ArticleImage.objects.create(article=article, image=img)
                    print(f"✅ 第{idx}张图片保存成功: {img.name}")
                except SuspiciousFileOperation as e:
                    error_msg = f"⚠️ 第{idx}张图片上传失败：{str(e)}"
                except Exception as e:
                    error_msg = f"⚠️ 第{idx}张图片上传失败：{str(e)}"

            if error_msg:
                return render(request, 'blog/article_create.html', {
                    'article_form': article_form,
                    'error': error_msg
                })

            return redirect('blog:index')
    else:
        article_form = ArticleForm()

    return render(request, 'blog/article_create.html', {
        'article_form': article_form,
        'error': ''
    })


# ========== 原有视图：首页（保留+优化头像显示） ==========
def index(request):
    articles = Article.objects.all().annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True),
        image_count=Count('images', distinct=True)
    ).prefetch_related('images', 'author__profile').order_by('-created_at')
    return render(request, 'blog/index.html', {'articles': articles})


# ========== 原有视图：搜索文章（保留） ==========
def search_articles(request):
    if request.method == 'GET' and 'keyword' in request.GET:
        keyword = request.GET.get('keyword').strip()
        articles = Article.objects.filter(title__icontains=keyword).annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True),
            image_count=Count('images', distinct=True)
        ).prefetch_related('images', 'author__profile').order_by('-created_at')
        return render(request, 'blog/search_result.html', {
            'articles': articles,
            'keyword': keyword
        })
    return redirect('blog:index')


# ========== 原有视图：文章详情（保留） ==========
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    article_images = article.images.all()
    print(f"📝 文章{article_id}的图片数量: {article_images.count()}")

    root_comments = Comment.objects.filter(article=article, parent=None).annotate(
        like_count=Count('likes', distinct=True),
        reply_count=Count('replies', distinct=True)
    ).order_by('-created_at')

    replies_queryset = Comment.objects.filter(parent__isnull=False).annotate(
        like_count=Count('likes', distinct=True)
    ).order_by('created_at')

    root_comments = root_comments.prefetch_related(
        Prefetch('replies', queryset=replies_queryset, to_attr='prefetched_replies'),
        'author__profile'
    )

    comment_form = CommentForm()
    reply_form = ReplyForm()

    user_liked_article = request.user.is_authenticated and Like.objects.filter(article=article, user=request.user).exists()

    user_comment_likes = []
    if request.user.is_authenticated:
        user_comment_likes = CommentLike.objects.filter(user=request.user).values_list('comment_id', flat=True)

    return render(request, 'blog/detail.html', {
        'article': article,
        'article_images': article_images,
        'root_comments': root_comments,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'user_liked_article': user_liked_article,
        'user_comment_likes': user_comment_likes,
    })


# ========== 原有视图：删除文章（保留） ==========
@login_required
def article_delete(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.author == request.user:
        article.delete()
    return redirect('blog:index')


# ========== 原有视图：添加评论（保留） ==========
@login_required
def add_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
    return redirect('blog:detail', article_id=article_id)


# ========== 原有视图：添加回复（保留） ==========
@login_required
def add_reply(request, article_id, comment_id):
    article = get_object_or_404(Article, id=article_id)
    parent_comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.article = article
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()
    return redirect('blog:detail', article_id=article_id)


# ========== 原有视图：文章点赞（保留） ==========
@login_required
def toggle_like(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    like, created = Like.objects.get_or_create(article=article, user=request.user)
    if not created:
        like.delete()
    return redirect('blog:detail', article_id=article_id)


# ========== 原有视图：评论点赞（保留） ==========
@login_required
def toggle_comment_like(request, article_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    if not created:
        like.delete()
    return redirect('blog:detail', article_id=article_id)


# ========== 原有视图：注册（保留） ==========
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})


# ========== 原有视图：登录（保留） ==========
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('blog:index')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})


# ========== 原有视图：注销（保留） ==========
@login_required
def user_logout(request):
    logout(request)
    return redirect('blog:index')


# ========== 新增：个人主页视图（整合修改用户名/密码/头像） ==========
@login_required
def profile(request, username=None):
    if not username:
        target_user = request.user
    else:
        target_user = get_object_or_404(User, username=username)

    profile, created = Profile.objects.get_or_create(user=target_user)
    user_articles = Article.objects.filter(author=target_user).annotate(
        like_count=Count('likes'),
        comment_count=Count('comments')
    ).order_by('-created_at')

    is_following = False
    if request.user.is_authenticated and request.user != target_user:
        is_following = request.user.profile.following.filter(id=target_user.id).exists()

    username_error = ''
    if request.method == 'POST' and 'new_username' in request.POST:
        new_username = request.POST.get('new_username', '').strip()
        if not new_username:
            username_error = "用户名不能为空！"
        elif new_username == target_user.username:
            username_error = "新用户名不能和原用户名相同！"
        elif User.objects.filter(username=new_username).exists() and new_username != target_user.username:
            username_error = "该用户名已被占用，请更换！"
        elif request.user == target_user:
            target_user.username = new_username
            target_user.save()
            return redirect('blog:profile_user', username=new_username)

    password_form = PasswordChangeForm(user=request.user)
    password_error = ''
    password_success = ''
    if request.method == 'POST' and 'old_password' in request.POST:
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid() and request.user == target_user:
            user = password_form.save()
            update_session_auth_hash(request, user)
            password_success = "密码修改成功！"
        else:
            password_error = "密码修改失败，请检查原密码是否正确！"

    avatar_error = ''
    if request.method == 'POST' and 'avatar' in request.FILES and request.user == target_user:
        avatar = request.FILES.get('avatar')
        try:
            if avatar and not avatar.content_type.startswith('image/'):
                avatar_error = "只能上传图片格式（jpg/png/gif）！"
            else:
                profile.avatar = avatar
                profile.save()
                avatar_error = "头像上传成功！"
        except Exception as e:
            avatar_error = f"上传失败：{str(e)}"

    context = {
        'target_user': target_user,
        'profile': profile,
        'user_articles': user_articles,
        'is_following': is_following,
        'username_error': username_error,
        'password_form': password_form,
        'password_error': password_error,
        'password_success': password_success,
        'avatar_error': avatar_error,
    }
    return render(request, 'blog/profile.html', context)


# ========== 新增：关注/取消关注视图 ==========
@login_required
def follow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.user == target_user:
        return redirect('blog:profile_user', username=target_user.username)

    if request.user.profile.following.filter(id=target_user.id).exists():
        request.user.profile.following.remove(target_user)
    else:
        request.user.profile.following.add(target_user)

    return redirect('blog:profile_user', username=target_user.username)


# ========== 新增：查看关注/粉丝列表 ==========
@login_required
def follow_list(request, username, list_type):
    target_user = get_object_or_404(User, username=username)
    if list_type == 'following':
        users = target_user.profile.following.all()
        title = f"{target_user.username}关注的人"
    elif list_type == 'followers':
        users = target_user.followers.all()
        title = f"{target_user.username}的粉丝"
    else:
        return redirect('blog:profile_user', username=username)

    context = {
        'target_user': target_user,
        'users': users,
        'title': title,
        'list_type': list_type,
    }
    return render(request, 'blog/follow_list.html', context)

# ========== 原有视图：修改用户名（已整合到profile，可删除或保留） ==========
@login_required
def edit_profile(request):
    if request.method == 'POST':
        new_username = request.POST.get('new_username', '').strip()
        if not new_username:
            error_msg = "用户名不能为空！"
        elif new_username == request.user.username:
            error_msg = "新用户名不能和原用户名相同！"
        elif User.objects.filter(username=new_username).exists() and new_username != request.user.username:
            error_msg = "该用户名已被占用，请更换！"
        else:
            request.user.username = new_username
            request.user.save()
            return redirect('blog:profile_success')

    return render(request, 'blog/edit_profile.html', {
        'error_msg': locals().get('error_msg', ''),
        'current_username': request.user.username
    })


# ========== 原有视图：修改成功提示页（保留） ==========
@login_required
def profile_success(request):
    return render(request, 'blog/profile_success.html')