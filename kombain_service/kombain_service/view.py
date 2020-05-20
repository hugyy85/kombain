from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, User
from django.contrib.auth import login, authenticate, logout, views as auth_views
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .forms import UploadFileForm
from .models import CallReport, CallReportTraffic


@login_required()
def home(request):
    return render(request, 'base.html')


def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_pwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_pwd)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/sign_up.html', {'form': form})


@login_required()
def create_report(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            CallReport().pdf_to_db(request.FILES['file'], request.user)
            return redirect('/listing')
    else:
        form = UploadFileForm()
    return render(request, 'report/creation.html', {'form': form})


@login_required()
def listing_reports(request):
    reports = CallReport.objects.filter(user_id=request.user.id)
    return render(request, 'report/listing.html', {'reports': reports})


@login_required()
def show_report(request, report_id, username):
    if username == request.user.username:
        report = CallReportTraffic.objects.filter(call_report_id=report_id)
        date_start = request.GET['date_start'] or report.order_by('date_time')[0].date_time
        date_end = request.GET['date_end'] or report.order_by('date_time').reverse()[0].date_time
        report = report.filter(date_time__lte=date_end, date_time__gte=date_start)
        if report.exists():
            internet_traffic = report.aggregate(Sum('traffic_int_volume'))['traffic_int_volume__sum'] // 1024  # in Mbytes
            calls = report.values('traffic_place')\
                .annotate(total_sec=Sum('traffic_sec_volume'))\
                .order_by('-total_sec')
        else:
            internet_traffic = None
            calls = None
        context = {
            'internet': internet_traffic,
            'calls': calls,
            'report': report_id
        }
    else:
        context = {'error': 'Доступ закрыт'}

    return render(request, 'report/report.html', context)
