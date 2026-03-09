from django.urls import path
from . import views  # 这一行必须有，否则找不到 views

app_name = 'blog'

urlpatterns = [
    # 首页
    path('', views.index, name='index'),

    # 文章相关
    path('create/', views.article_create, name='create'),
    path('detail/<int:article_id>/', views.article_detail, name='detail'),
    path('delete/<int:article_id>/', views.article_delete, name='delete'),

    # 点赞相关
    path('toggle-like/<int:article_id>/', views.toggle_like, name='toggle_like'),
    path('toggle-comment-like/<int:article_id>/<int:comment_id>/', views.toggle_comment_like,
         name='toggle_comment_like'),

    # 评论/回复相关
    path('add-comment/<int:article_id>/', views.add_comment, name='add_comment'),
    path('add-reply/<int:article_id>/<int:comment_id>/', views.add_reply, name='add_reply'),

    # 用户认证相关
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # 用户修改名称相关（保留，也可后续整合到profile后删除）
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile-success/', views.profile_success, name='profile_success'),

    # 搜索功能
    path('search/', views.search_articles, name='search'),

    # ========== 新增：个人主页 + 关注功能相关URL ==========
    # 自己的个人主页
    path('profile/', views.profile, name='profile'),
    # 他人的个人主页（通过用户名访问）
    path('profile/<str:username>/', views.profile, name='profile_user'),
    # 关注/取消关注用户
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    # 查看关注列表/粉丝列表（list_type: following/followers）
    path('profile/<str:username>/<str:list_type>/', views.follow_list, name='follow_list'),
]