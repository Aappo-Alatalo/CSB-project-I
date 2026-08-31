from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm, ReservationForm
from .models import Profile, Reservation


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'bookings/home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                apartment=form.cleaned_data['apartment'],
                phone=form.cleaned_data['phone'],
            )
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'bookings/register.html', {'form': form})


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        error = 'Wrong username or password.'
    return render(request, 'bookings/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    reservations = request.user.reservations.all()
    return render(request, 'bookings/dashboard.html', {'reservations': reservations})


@login_required
def book(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            return redirect('dashboard')
    else:
        form = ReservationForm()
    return render(request, 'bookings/book.html', {'form': form})


@login_required
def reservation_detail(request, pk):
    # FLAW 1 (A01 Broken Access Control / IDOR): the reservation is fetched by primary key only,
    # with no check that it belongs to the logged-in resident. By changing the id in the URL a
    # resident can force-browse to any other resident's booking and see who has the sauna and when.
    # The same missing check is what lets cancel_reservation() below delete other people's shifts.
    reservation = Reservation.objects.get(pk=pk)
    # FIX (A01): scope the lookup to the current user so residents can only open their own bookings
    # (a missing or non-owned reservation then returns 404).
    # reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    return render(request, 'bookings/reservation_detail.html', {'reservation': reservation})


@login_required
def cancel_reservation(request, pk):
    # FLAW 1 (A01 Broken Access Control / IDOR): the reservation is fetched by primary key only,
    # with no ownership check, so a resident can cancel and delete ANY other resident's shift just
    # by posting its id - unauthorized modification and destruction of data they do not own.
    reservation = Reservation.objects.get(pk=pk)
    # FIX (A01): only let a resident cancel their own reservation (otherwise return 404).
    # reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        reservation.delete()
        return redirect('dashboard')
    return render(request, 'bookings/cancel.html', {'reservation': reservation})


@login_required
def directory(request):
    q = request.GET.get('q', '')
    residents = []
    if q:
        # FLAW 3 (A03 Injection): the search term is concatenated straight into the SQL string, so
        # an attacker can break out of the string literal and run their own SQL. For example
        # searching  ' UNION SELECT username, password, '' FROM auth_user --  dumps every username
        # and password hash into the results.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT full_name, apartment, phone FROM bookings_profile "
                "WHERE full_name LIKE '%" + q + "%'"
            )
            residents = cursor.fetchall()
        # FIX (A03): let the ORM build a parameterized query so the search term is always treated as
        # data, never as SQL. values_list keeps the (name, apartment, phone) tuples the template
        # expects. Comment out the raw query above and uncomment the line below.
        # residents = Profile.objects.filter(full_name__icontains=q).values_list(
        #     'full_name', 'apartment', 'phone')
    return render(request, 'bookings/directory.html', {'residents': residents, 'q': q})
