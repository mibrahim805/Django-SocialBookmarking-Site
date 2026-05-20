from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from bs4 import BeautifulSoup
from bookmark.forms import BookmarkForm, CustomUserCreationForm
from bookmark.models import Bookmarks, Follow, CustomUser, Tags
from bookmark.forms import BookmarkImportForm


# Create your views here.


def register_view(request):
    if request.user.is_authenticated:
        return redirect('bookmark_list')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'bookmark/register.html', {'form': form})




@login_required
def bookmark_create_view(request):
    if request.method == 'POST':
        form = BookmarkForm(request.POST)
        if form.is_valid():
            bookmark = form.save(commit=False)
            bookmark.user = request.user
            bookmark.save()
            form.save()
            return redirect('bookmark_list')
    else:
        form = BookmarkForm()
    return render(request, "bookmark/add_bookmark.html", {"form": form})


@login_required
def bookmark_list_view(request):
    bookmarks = Bookmarks.objects.filter(is_public=True).order_by('-created_at')
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    return render(request,"bookmark/bookmark_list.html",{"bookmarks":bookmarks, "following_ids":following_ids, "view_type": "all"})


@login_required
def my_bookmarks_view(request):
    bookmarks = Bookmarks.objects.filter(user=request.user).order_by('-created_at')
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    return render(request,"bookmark/bookmark_list.html",{"bookmarks":bookmarks, "following_ids":following_ids, "view_type": "my"})


@login_required
def search_bookmarks_view(request):
    query = request.GET.get('q', '').strip()
    bookmarks = []
    if query:
        bookmarks = Bookmarks.objects.filter(Q(is_public=True) & (
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__name__icontains=query))).distinct().order_by('-created_at')
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    return render(request,"bookmark/bookmark_list.html",{"bookmarks": bookmarks,"following_ids": following_ids,"view_type": "search","search_query": query})



@login_required
def user_follow_view(request, user_id):
    follower = request.user
    following = get_object_or_404(CustomUser, id=user_id)
    follow = Follow.objects.filter(follower=follower, following=following).first()
    if follow:
        follow.delete()
    else:
        Follow.objects.create(follower=follower, following=following)
    return redirect("bookmark_list")





def parse_html_bookmarks(file_content):
    bookmarks = []
    try:
        soup = BeautifulSoup(file_content, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            url = link.get('href', '').strip()
            title = link.get_text(strip=True)
            tags_str = link.get('tags', '')
            tags = []
            for t in tags_str.split(','):
                t = t.strip()
                if t:
                    tags.append(t)
            if title and url:
                bookmarks.append({
                    'title': title,
                    'url': url,
                    'tags': tags})
        return bookmarks
    except Exception:
        return None



@login_required
def import_bookmarks(request):
    if request.method == 'POST':
        form = BookmarkImportForm(request.POST,request.FILES)
        if form.is_valid():
            try:
                html_file = request.FILES['html_file']
                if html_file.size > 5 * 1024 * 1024:
                    messages.error(request,'File size must be less than 5MB')
                    return render(request,'bookmark/import_bookmarks.html',{'form': form})
                content = html_file.read().decode('utf-8',errors='ignore')
                bookmarks_data = parse_html_bookmarks(content)
                if bookmarks_data is None:
                    messages.error(request,'Invalid bookmark HTML file.')
                    return render(request,'bookmark/import_bookmarks.html',{'form': form})
                if not bookmarks_data:
                    messages.warning(request,'No bookmarks found.')
                    return render(request,'bookmark/import_bookmarks.html',{'form': form})
                imported_count = 0
                skipped_count = 0
                is_public = form.cleaned_data.get('is_public',True)
                for bookmark_data in bookmarks_data:
                    url = bookmark_data['url']
                    title = bookmark_data['title']
                    tags = bookmark_data['tags']
                    if not url.startswith(('http://', 'https://', 'ftp://')):
                        skipped_count += 1
                        continue
                    if Bookmarks.objects.filter(user=request.user,url=url).exists():
                        skipped_count += 1
                        continue
                    bookmark = Bookmarks.objects.create(user=request.user,title=title[:200],url=url[:500],description='Imported from browser',is_public=is_public)
                    for tag_name in tags[:5]:
                        tag_name = tag_name.strip()[:50]
                        if tag_name:
                            tag, created = Tags.objects.get_or_create(name=tag_name)
                            bookmark.tags.add(tag)
                    imported_count += 1
                messages.success(request,f'Successfully imported 'f'{imported_count} bookmarks 'f'({skipped_count} skipped)')
                return redirect('my_bookmarks')
            except Exception as e:
                messages.error(request,f'Error: {str(e)}')
                return render(request,'bookmark/import_bookmarks.html',{'form': form})
    else:
        form = BookmarkImportForm()
    return render(request,'bookmark/import_bookmarks.html',{'form': form})









