from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from taggit.models import Tag
from django.db.models import Count

from .forms import EmailPostForm, CommentForm
from .models import Post, Comment


# Create your views here.
def post_list(request, tag_slug=None):
    object_list = Post.publish.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags_in=[tag])

    paginator = Paginator(object_list, 3)  # 3 статьи на странице
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом - возвращаем первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если номер стр больше, чем общее кол-во страниц - возвращаем последнюю стр
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html',
                  {
                      'page': page,
                      'posts': posts,
                      'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    # список активных комментариев для этой статьи:
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # пользователь отправил комментарий:
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # создаем комментарий, но пока не сохраняем в базе данных:
            new_comment = comment_form.save(commit=False)
            # привязываем комментарий к текущей статье
            new_comment.post = post
            # сохраняем комментарий к текущей статье
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


def post_share(request, post_id):
    # получение поста по id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # форма сохранена
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # все поля валидны
            cd = form.cleaned_data
            # отправка почты
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}/{}/{}[comments]:'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',
                  {'post': post, 'form': form, 'sent': sent})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
