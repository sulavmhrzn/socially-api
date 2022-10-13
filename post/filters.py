import django_filters

from .models import Post


class PostFilterSet(django_filters.FilterSet):
    class Meta:
        model = Post
        fields = ["author__username", "title"]
