from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

from .forms import EmailPostForm
from .models import Post


# Create your views here.
def post_list(request):
    object_list = Post.publish.all()
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
                      'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})


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
