from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Resource
from .forms import ResourceForm
from notes.models import Category
from dashboard.models import log_activity

@login_required
def resource_list(request):
    resources = Resource.objects.filter(user=request.user).select_related('category')

    # Search Query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Resource Type Filter
    type_filter = request.GET.get('type', '').strip()
    if type_filter:
        resources = resources.filter(resource_type=type_filter)

    # Category Filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter.isdigit():
        resources = resources.filter(category_id=category_filter)

    # Sorting
    sort_by = request.GET.get('sort', 'newest').strip()
    SORT_MAP = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'title_asc': 'title',
        'title_desc': '-title',
    }
    ordering = SORT_MAP.get(sort_by, '-created_at')
    resources = resources.order_by(ordering)

    # Pagination (10 resources per page)
    paginator = Paginator(resources, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(user=request.user)
    resource_types = Resource.RESOURCE_TYPE_CHOICES

    return render(request, 'resources/resource_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'categories': categories,
        'resource_types': resource_types,
        'total_count': resources.count(),
    })


@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    return render(request, 'resources/resource_detail.html', {'resource': resource})


@login_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, user=request.user)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.user = request.user
            resource.save()
            log_activity(request.user, 'RESOURCE_CREATED', f"Added learning resource '{resource.title}'")
            messages.success(request, f"Resource '{resource.title}' added successfully!")
            return redirect('resources:resource_list')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ResourceForm(user=request.user)

    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'Add New Resource'})


@login_required
def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource, user=request.user)
        if form.is_valid():
            resource = form.save()
            log_activity(request.user, 'RESOURCE_UPDATED', f"Updated resource '{resource.title}'")
            messages.success(request, f"Resource '{resource.title}' updated successfully!")
            return redirect('resources:resource_detail', pk=resource.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ResourceForm(instance=resource, user=request.user)

    return render(request, 'resources/resource_form.html', {'form': form, 'resource': resource, 'title': 'Edit Resource'})


@login_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == 'POST':
        title = resource.title
        resource.delete()
        log_activity(request.user, 'RESOURCE_DELETED', f"Deleted resource '{title}'")
        messages.success(request, f"Resource '{title}' deleted successfully!")
        return redirect('resources:resource_list')

    return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})
