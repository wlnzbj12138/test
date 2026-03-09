from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # 引入博客应用的 URL 配置（不要直接导入 views）
    path('', include('blog.urls')),
]

# 开发环境下映射媒体文件 URL（支持图片访问）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)