from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from admins.forms import (
    CreateUserForm,
    ProductRequestForm,
    createProductForm,
    editProductForm,
    editUserForm,
)
from .models import (
    Product,
    ProductRequest,
    ProductRequestAdmin,
    ProductRequestSystem,
    UserProfile,
)


def _role_denied(request, *allowed_roles):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = getattr(request.user, 'userprofile', None)
    if profile is None or profile.role not in allowed_roles:
        return redirect('index')
    return None


def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


def admin_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = getattr(request.user, 'userprofile', None)
    if profile is None:
        return redirect('login')

    if profile.role == 'boshliq':
        return render(request, 'boshliq/home.html')
    if profile.role == 'admin':
        return render(request, 'admin/base_admin.html')
    if profile.role == 'sotuvchi':
        return render(request, 'sotuvchi/home.html')
    return redirect('login')


def shop(request):
    return render(request, 'shop.html')


def table_page(request):
    denied = _role_denied(request, 'admin', 'boshliq')
    if denied:
        return denied
    return render(request, 'admin/base_table.html', {'product': Product.objects.all()})


def create_table(request):
    denied = _role_denied(request, 'admin', 'boshliq')
    if denied:
        return denied

    if request.method == 'POST':
        form = createProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('table_page')
    else:
        form = createProductForm()
    return render(request, 'admin/create.html', {'form': form})


@require_POST
def delete_product(request, pk):
    denied = _role_denied(request, 'admin', 'boshliq')
    if denied:
        return denied
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('table_page')


def edit_product(request, pk):
    denied = _role_denied(request, 'admin', 'boshliq')
    if denied:
        return denied
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = editProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('table_page')
    else:
        form = editProductForm(instance=product)
    return render(request, 'admin/edit.html', {'form': form, 'product': product})


def create_user(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = getattr(request.user, 'userprofile', None)
    if profile is None or profile.role not in ['boshliq', 'admin']:
        return redirect('admin_page')

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            rating = form.cleaned_data['raiting']
            phone_number = form.cleaned_data['phonenumber']

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'This username already exists.')
            else:
                user = User.objects.create_user(username=username, password=password)
                UserProfile.objects.create(
                    phonenumber=phone_number,
                    user=user,
                    role=role,
                    raiting=rating,
                )
                return redirect('admin_page')
    else:
        form = CreateUserForm()
    return render(request, 'create_user.html', {'form': form})


def admins(request):
    denied = _role_denied(request, 'boshliq', 'admin')
    if denied:
        return denied
    profile = getattr(request.user, 'userprofile', None)
    context = {
        'admin_soni': UserProfile.objects.filter(role='admin').count(),
        'sotuvchi_soni': UserProfile.objects.filter(role='sotuvchi').count(),
        'product_soni': Product.objects.count(),
        'username': request.user.username,
        'foydalanuvchilar': UserProfile.objects.select_related('user').all(),
        'profile': profile,
    }
    return render(request, 'boshliq/admins.html', context)


def hisobot(request):
    denied = _role_denied(request, 'boshliq', 'admin')
    if denied:
        return denied
    context = {
        'product_soni': Product.objects.count(),
        'admin_soni': UserProfile.objects.filter(role='admin').count(),
        'sotuvchi_soni': UserProfile.objects.filter(role='sotuvchi').count(),
        'username': request.user.username,
    }
    return render(request, 'boshliq/hisobot.html', context)


def foydalanuvchilar(request):
    denied = _role_denied(request, 'boshliq', 'admin')
    if denied:
        return denied
    return render(request, 'boshliq/users.html')


def boshliq_page(request):
    denied = _role_denied(request, 'boshliq', 'admin')
    if denied:
        return denied
    return render(request, 'boshliq/home.html')


def edit_user(request, pk):
    
    profile = UserProfile.objects.get(user__pk=pk)
    if request.method == 'POST':
        form = editUserForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('admins')
    else:
        form = editUserForm(instance=profile)
    return render(request, 'boshliq/edit_user.html', {'form': form, 'profile': profile})


@require_POST
def delete_user(request, pk):
    denied = _role_denied(request, 'boshliq', 'admin')
    if denied:
        return denied
    profile = get_object_or_404(UserProfile, pk=pk)
    profile.user.delete()
    return redirect('admins')


def seller_page(request):
    denied = _role_denied(request, 'sotuvchi')
    if denied:
        return denied

    if request.method == 'POST':
        form = ProductRequestForm(request.POST, request.FILES)
        if form.is_valid():
            product_request = form.save(commit=False)
            product_request.user = request.user.userprofile
            product_request.save()
            ProductRequestSystem.objects.get_or_create(
                product_request=product_request,
                defaults={'status': 'pending'},
            )
            return redirect('sotuvchi_page')
    else:
        form = ProductRequestForm()

    return render(request, 'sotuvchi/product_jonatish.html', {'form': form})


def product_requests(request):
    denied = _role_denied(request, 'admin', 'boshliq')
    if denied:
        return denied
    requests = ProductRequest.objects.select_related('user').order_by('-id')
    return render(request, 'admin/admin_requests.html', {'requests': requests})


def _update_request_status(request, pk, status_value, comment=''):
    denied = _role_denied(request, 'admin', 'boshliq')
    if denied:
        return denied

    product_request = get_object_or_404(ProductRequest, pk=pk)
    system, _ = ProductRequestSystem.objects.get_or_create(
        product_request=product_request,
        defaults={'status': 'pending'},
    )
    system.status = status_value
    system.save()

    review, _ = ProductRequestAdmin.objects.get_or_create(
        product_request=product_request,
    )
    review.admincoment = comment
    review.tekshirgan = request.user
    review.tekshirilganvaqt = timezone.now()
    review.save()
    return redirect('product_requests')


@require_POST
def qabul_product(request, pk):
    return _update_request_status(request, pk, 'approved')


@require_POST
def rad_product(request, pk):
    return _update_request_status(request, pk, 'rejected', 'Hato malumot!')


@require_POST
def tuzatish_product(request, pk):
    return _update_request_status(request, pk, 'needs_fix', 'Tuzatish kerak.')
