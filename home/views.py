from django.http.response import StreamingHttpResponse
from django.shortcuts import redirect, render, HttpResponse
from django.core.serializers import serialize
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from home.models import Place, Record, Doctor
from home.sd_be.sda_api import *
from home.sd_be_fm.face_mask_api import *
from django_pandas.io import read_frame
import mimetypes
from datetime import datetime


# Create your views here.
def test(request):
    return render(request, 'test.html')


def notify_user(request):
    res = Place.objects.filter(is_alert=True).values()
    return JsonResponse({"results": list(res)})


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request, loc_id=0):
    loc = Place.objects.filter(pk=loc_id)[0]
    Place.objects.filter(pk=loc_id).update(is_alert=False)
    # loc.is_alert = False
    return StreamingHttpResponse(gen(StreamingCamera(location=loc)),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def face_mask_feed(request):
    return StreamingHttpResponse(gen(StreamingFaceMask()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


#######################
def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.info(request, 'Username OR password incorrect')

    return render(request, "index.html")


def home(request):
    return render(request, "home.html")


def records(request):
    record_list = Record.objects.all()
    return render(request, "records.html", context={"records": record_list})


def download_report(request):
    # read the records from the database
    m_records = Record.objects.all()
    # convert it into dataframe
    df = read_frame(m_records)
    # set a unique filename
    file_name = f'record_{datetime.now().strftime("%d-%m-%Y__%H-%M-%S")}.csv'
    # save the dataframe to csv
    df.to_csv(file_name)
    # open the file
    path = open(file_name, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(file_name)
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % file_name
    # Return the response value
    return response


def doctors_contact(request):
    doctors = Doctor.objects.all()
    return render(request, "doctors-contact.html", context={
        "doctors": doctors
    })


def forgot_password(request):
    return render(request, "forgot-password.html")


def edit_account(request):
    return render(request, "edit-account.html")


def location1(request):
    return render(request, "location-1.html")


def location2(request):
    return render(request, "location-2.html")


def location3(request):
    return render(request, "location-3.html")


def location4(request):
    return render(request, "location-4.html")


def location5(request):
    return render(request, "location-5.html")
