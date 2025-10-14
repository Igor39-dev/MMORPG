from django_filters import FilterSet

from board.models import Reply, Post


class ReplyFilter(FilterSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = kwargs['request']
        self.filters['post'].label = 'Посты'
        self.filters['post'].queryset = Post.objects.filter(user=self.user)

    class Meta:
        model = Reply
        fields = ['post']
