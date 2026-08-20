from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Note, Category, Tag
from .forms import NoteForm, CategoryForm, TagForm
from dashboard.models import log_activity

@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user).select_related('category').prefetch_related('tags')

    # Search Query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    # Category Filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter.isdigit():
        notes = notes.filter(category_id=category_filter, category__user=request.user)

    # Tag Filter
    tag_filter = request.GET.get('tag', '').strip()
    if tag_filter.isdigit():
        notes = notes.filter(tags__id=tag_filter, tags__user=request.user)

    # Sorting Whitelist
    sort_by = request.GET.get('sort', 'updated').strip()
    SORT_MAP = {
        'updated': '-updated_at',
        'newest': '-created_at',
        'oldest': 'created_at',
        'title_asc': 'title',
        'title_desc': '-title',
    }
    ordering = SORT_MAP.get(sort_by, '-updated_at')
    notes = notes.order_by(ordering)

    # Pagination (10 notes per page)
    paginator = Paginator(notes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(user=request.user)
    tags = Tag.objects.filter(user=request.user)

    return render(request, 'notes/note_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'tag_filter': tag_filter,
        'sort_by': sort_by,
        'categories': categories,
        'tags': tags,
        'total_count': notes.count(),
    })


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})


@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            form.save_m2m()  # Save M2M tags
            log_activity(request.user, 'NOTE_CREATED', f"Created note '{note.title}'")
            messages.success(request, f"Note '{note.title}' created successfully!")
            return redirect('notes:note_list')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = NoteForm(user=request.user)

    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Create New Note'})


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.save()
            form.save_m2m()
            log_activity(request.user, 'NOTE_UPDATED', f"Updated note '{note.title}'")
            messages.success(request, f"Note '{note.title}' updated successfully!")
            return redirect('notes:note_detail', pk=note.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = NoteForm(instance=note, user=request.user)

    return render(request, 'notes/note_form.html', {'form': form, 'note': note, 'title': 'Edit Note'})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        title = note.title
        note.delete()
        log_activity(request.user, 'NOTE_DELETED', f"Deleted note '{title}'")
        messages.success(request, f"Note '{title}' deleted successfully!")
        return redirect('notes:note_list')

    return render(request, 'notes/note_confirm_delete.html', {'note': note})


# Category Views
@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f"Category '{category.name}' added!")
            return redirect('notes:category_list')
    else:
        form = CategoryForm(user=request.user)

    return render(request, 'notes/category_list.html', {
        'categories': categories,
        'form': form
    })


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated!")
            return redirect('notes:category_list')
    else:
        form = CategoryForm(instance=category, user=request.user)

    return render(request, 'notes/category_form.html', {'form': form, 'category': category})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted!")
        return redirect('notes:category_list')

    return render(request, 'notes/category_confirm_delete.html', {'category': category})


# Tag Views
@login_required
def tag_list(request):
    tags = Tag.objects.filter(user=request.user)
    if request.method == 'POST':
        form = TagForm(request.POST, user=request.user)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            messages.success(request, f"Tag '{tag.name}' added!")
            return redirect('notes:tag_list')
    else:
        form = TagForm(user=request.user)

    return render(request, 'notes/tag_list.html', {'tags': tags, 'form': form})


@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk, user=request.user)
    if request.method == 'POST':
        name = tag.name
        tag.delete()
        messages.success(request, f"Tag '{name}' deleted!")
        return redirect('notes:tag_list')

    return redirect('notes:tag_list')
