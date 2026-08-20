from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse, reverse_lazy

from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile


signer = TimestampSigner()

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Generate Email Verification Token
            token = signer.sign(user.pk)
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'token': token})
            )

            # Send Email Verification
            send_mail(
                subject='Welcome to AI Study Hub - Verify Your Email',
                message=f'Hi {user.username},\n\nThank you for registering at AI Study Hub!\nPlease click the link below to verify your email address:\n\n{verification_url}\n\nHappy Learning!',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@aistudyhub.com'),
                recipient_list=[user.email],
                fail_silently=True,
            )

            messages.success(request, 'Account created successfully! Please check your email to verify your account and log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if input is email or username
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(request, username=username_or_email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Invalid username/email or password.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Compute user study statistics safely
    stats = {
        'total_tasks': request.user.tasks.count(),
        'completed_tasks': request.user.tasks.filter(is_completed=True).count(),
        'total_notes': request.user.notes.count(),
        'total_resources': request.user.resources.count(),
        'total_quizzes': request.user.quizzes.count(),
    }

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'stats': stats,
    })


@login_required
def edit_profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user, user=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors in the profile form.')
    else:
        user_form = UserUpdateForm(instance=request.user, user=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


def verify_email_view(request, token):
    try:
        user_id = signer.unsign(token, max_age=86400) # Valid for 24 hours
        user = get_object_or_404(User, pk=user_id)
        profile, created = Profile.objects.get_or_create(user=user)
        if profile.is_email_verified:
            messages.info(request, 'Your email address is already verified.')
        else:
            profile.is_email_verified = True
            profile.save()
            messages.success(request, 'Your email address has been successfully verified!')
    except SignatureExpired:
        messages.error(request, 'Verification link has expired. Please request a new link.')
    except (BadSignature, ValueError):
        messages.error(request, 'Invalid email verification link.')

    if request.user.is_authenticated:
        return redirect('accounts:profile')
    return redirect('accounts:login')


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                "If an account exists with the email address you entered, a password reset link has been sent to your email."
            )
            return response
        except Exception as e:
            messages.error(
                self.request,
                f"Failed to send password reset email via SMTP ({str(e)}). Please verify your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD credentials in .env."
            )
            return self.form_invalid(form)


class CustomPasswordResetConfirmView(SuccessMessageMixin, auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    success_message = "Your password has been reset successfully. You can now log in with your new password."


