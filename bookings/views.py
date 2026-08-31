from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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
    # FLAW 1 (A01 Broken Access Control / IDOR): the reservation is fetched by primary key only.
    # There is no check that it belongs to the logged-in resident, so anyone can read another
    # resident's booking - including the private note - by changing the id in the URL.
    reservation = Reservation.objects.get(pk=pk)
    # FIX (A01): scope the lookup to the current user so other residents' bookings are not exposed
    # (a missing object then returns 404 instead of leaking data).
    # reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    return render(request, 'bookings/reservation_detail.html', {'reservation': reservation})


@login_required
def cancel_reservation(request, pk):
    # FLAW 1 (A01 Broken Access Control / IDOR): the reservation is fetched by primary key only,
    # with no ownership check, so a resident can cancel anyone's shift by posting its id.
    reservation = Reservation.objects.get(pk=pk)
    # FIX (A01): only let a resident cancel their own reservation.
    # reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        reservation.delete()
        return redirect('dashboard')
    return render(request, 'bookings/cancel.html', {'reservation': reservation})
