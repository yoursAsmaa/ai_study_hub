from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import Task
from .forms import TaskForm
from notes.models import Category
from dashboard.models import log_activity

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    # Search Query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Status Filter
    status_filter = request.GET.get('status', '').strip()
    if status_filter == 'PENDING':
        tasks = tasks.filter(Q(status=Task.STATUS_PENDING) | Q(status=Task.STATUS_IN_PROGRESS), is_completed=False)
    elif status_filter == 'COMPLETED':
        tasks = tasks.filter(Q(status=Task.STATUS_COMPLETED) | Q(is_completed=True))

    # Priority Filter
    priority_filter = request.GET.get('priority', '').strip()
    if priority_filter in [Task.PRIORITY_LOW, Task.PRIORITY_MEDIUM, Task.PRIORITY_HIGH]:
        tasks = tasks.filter(priority=priority_filter)

    # Category Filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter.isdigit():
        tasks = tasks.filter(category_id=category_filter)

    # Overdue Filter
    overdue_filter = request.GET.get('overdue', '').strip()
    if overdue_filter == '1':
        tasks = tasks.filter(due_date__lt=timezone.now(), is_completed=False).exclude(status=Task.STATUS_COMPLETED)

    # Sorting
    sort_by = request.GET.get('sort', 'due_date').strip()
    if sort_by == 'priority':
        tasks = tasks.order_by('-priority', 'due_date')
    elif sort_by == 'created':
        tasks = tasks.order_by('-created_at')
    elif sort_by == 'status':
        tasks = tasks.order_by('status', 'due_date')
    else:
        # Default: upcoming due dates first (nulls last)
        tasks = tasks.order_by('due_date', '-priority')

    # Pagination (10 items per page)
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(user=request.user)

    return render(request, 'planner/task_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'overdue_filter': overdue_filter,
        'sort_by': sort_by,
        'categories': categories,
        'total_count': tasks.count(),
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'planner/task_detail.html', {'task': task})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            if task.status == Task.STATUS_COMPLETED:
                task.is_completed = True
            task.save()
            log_activity(request.user, 'TASK_CREATED', f"Created task '{task.title}'")
            messages.success(request, f"Task '{task.title}' created successfully!")
            return redirect('planner:task_list')
        else:
            messages.error(request, "Please correct errors in the task form.")
    else:
        form = TaskForm(user=request.user)

    return render(request, 'planner/task_form.html', {'form': form, 'title': 'Create New Task'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            if task.status == Task.STATUS_COMPLETED:
                task.is_completed = True
            else:
                task.is_completed = False
            task.save()
            log_activity(request.user, 'TASK_UPDATED', f"Updated task '{task.title}'")
            messages.success(request, f"Task '{task.title}' updated successfully!")
            return redirect('planner:task_list')
        else:
            messages.error(request, "Please correct errors in the task form.")
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, 'planner/task_form.html', {'form': form, 'task': task, 'title': 'Edit Task'})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        title = task.title
        task.delete()
        log_activity(request.user, 'TASK_DELETED', f"Deleted task '{title}'")
        messages.success(request, f"Task '{title}' deleted successfully!")
        return redirect('planner:task_list')

    return render(request, 'planner/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_status(request, pk):
    if request.method != 'POST':
        return redirect('planner:task_list')

    task = get_object_or_404(Task, pk=pk, user=request.user)
    if task.is_completed or task.status == Task.STATUS_COMPLETED:
        task.status = Task.STATUS_PENDING
        task.is_completed = False
        action_text = "marked as pending"
    else:
        task.status = Task.STATUS_COMPLETED
        task.is_completed = True
        action_text = "marked as completed"

    task.save()
    log_activity(request.user, 'TASK_STATUS_TOGGLED', f"Task '{task.title}' {action_text}")
    messages.success(request, f"Task '{task.title}' {action_text}.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('planner:task_list')
