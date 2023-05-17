from django.shortcuts import render, redirect
from django.db.models import Count
from datetime import datetime, timedelta
from .models import *
from django.contrib import messages
from django.conf import settings
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.conf.urls.static import static
    
def service_times(service):
    # Handling timing logic for each service
    if service == "Nephrology":
        times = {
                "Monday": ["11:30 AM"],
                "Wednesday": ["2 PM"]
                }
    elif service == "Dermatology":
            times = {
                "Tuesday": ["2 PM"]
                }
    elif service in ["Anaesthesia and Critical Care Medicine"]:
            times = {
                "Wednesday": ["9 AM","2 PM"]
                }
    elif service in ["Adult Neurology"]:
            times = {
                "Wednesday": ["9 AM","2 PM"]
                }
    elif service == "Interventional Cardiology":
            times = {
                "Saturday": ["10 AM"]
                }
    elif service == "Anaesthesia":
            times = {
                "Thursday": ["11 AM"]
                }
    elif service == "Radiology":
            times = {
                "Thursday": ["10 AM"]
                }
    elif service == "General Surgery":
            times = {
                "Monday": ["1:30 PM"],
                "Tuesday": ["1:30 PM"],
                "Wednesday": ["1:30 PM"],
                "Thursday": ["1:30 PM"]
                }
    elif service == "Ophthalmology":
            times = {
                "Tuesday": ["2 PM"]
                }
    elif service == "Ear, Nose and Throat (ENT)":
            times = {
                "Monday": ["10 AM"],
                "Tuesday":["2 PM"],
                "Wednesday": ["2 PM"],
                "Saturday":["9 AM"]
                }
    elif service == "Physician / Internal Medicine":
            times = {
                "Monday": ["10 AM"],
                "Thursday": ["9 AM", "11 AM"],
                "Saturday": ["2 PM"]
                }
    elif service == "Paediatrics and Child Health":
            times = {
                "Monday": ["8 AM"],
                "Tuesday": ["9 AM"],
                "Wednesday": ["10 AM"],
                "Thursday": ["8 AM"]
                }
    elif service == "Adult Cardiology":
            times = {
                "Thursday": ["8 AM", "12 PM"],
                "Saturday": ["2 PM"]
            }
    elif service == "Pain Management":
            times = {
                "Thursday": ["11 AM"]
            }
    elif service == "Gynaecology / Laparoscopic / Obsterics":
            times = {
                "Monday": ["10 AM"],
                "Tuesday": ["9 AM"]
            }
        
    return times    

def index(request):
    return render(request, "index.html",{})

def assign_doctor(appears, doctors):
    """Logic for assigning a doctor. I obtain a frequency queryset from the 
        appointments object on 'assigned_doctor', filter out values that have not appeared global least
        and randomly select the the index value of the remaining values in the doctors list 
    """
    for i, j in appears.items():
        if j != min(appears.values()):
            try:
                doctors.remove(i)
            except ValueError:
                pass
        
            
    if len(doctors) == 1:
        assigned_doctor = doctors[0]
    else:
        try:
            from random import randint
            idx = randint(0, (len(doctors)-1))            
            assigned_doctor = doctors[idx]
        except IndexError:
            pass
    return assigned_doctor    
            


def booking(request):
    
    """Function that applies the necessar business logic required in booking only available time slots within a 21-day period"""
    #Calling 'getServices' function to retrieve a list of all the available services
    services = getServices()
    assigned_doctor = ""
    times = {}

    if request.method == 'POST':
        service = request.POST.get('service')
        if service == None:
            messages.success(request, "Please Select A Service!")
            return redirect('booking')
        
        #Calling 'service_times' to only display times for the required service
        times = service_times(service)
        
        #Calling 'validWeekday' Function to Loop days you want in the next 21 days:
        weekdays = validWeekday(22)

        #Only show the days that are not full:
        validWorkdays = isWeekdayValid(weekdays, service, times)
        
        print(f"TIMES: {times}\nSERVICE: {service}\nVALID WORKDAYS{validWorkdays}")
        
        
        
        #Filter to retrieve only available times from each date before displaying them to the user
        appointments = Appointment.objects.filter(service=service)
        
        #Retrieve Doctor names from the filtered Doctor objects
        doctors= []
        service_doctors = Doctor.objects.filter(role=service).values_list("name") 
        appears = appointments.values_list('assigned_doctor').annotate(frequency = Count('assigned_doctor'))
        
        for doctor in service_doctors:
            doctors.append(doctor[0])

        appears = dict(appears)
        
        assigned_doctor = assign_doctor(appears=appears, doctors=doctors)
        
        print(f"{appears} {doctors}\nASSIGNED DOCTOR-> {assigned_doctor}")
        
        
        for item in appointments:
            print(item.service, item.assigned_doctor, item.day)
    
        if appointments.exists():    
            for item in appointments:
                appointment_date = item.day
                appointment_day = dayToWeekday(str(appointment_date))
                if appointment_date in [date.split()[0] for date in validWorkdays]:    
                    validWorkdays.remove(appointment_date+' '+appointment_day+' '+item.time)
                    pass
                
        
        print(f"THE APPOINTMENT FORMAT {appointments}, \nTHE DOCTORS ARE:{doctors}")
    
        #Store day, service and times data in django session:
        request.session['service'] = service
        request.session['assigned_doctor'] = assigned_doctor
        request.session['times'] = times
        request.session['validWorkdays'] = validWorkdays
        
        return redirect('bookingSubmit')


    return render(request, 'booking.html', {
            'times': times,
            'services': services,
        })

def bookingSubmit(request):
    user = request.user
    
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    
    #Get stored data from django session:
    service = request.session.get('service')
    validWorkdays = request.session.get('validWorkdays')
    assigned_doctor = request.session.get('assigned_doctor')
    
    #Handle pricing on a seperate thread
    if service in ["Nephrology", "Physician /Internal Medicine", "Ear, Nose and Throat (ENT)","Dermatology", "Adult Neurology", "General Surgery", "Paediatrics and Child Health", "Pain Management", "Gynaecology / Laparoscopic / Obsterics", "Ophthalmology", "Radiology"]:
        request.session['price'] = 2500
    elif service in ["Adult Cardiology", "Interventional Cardiology"]:
        request.session['price'] = 3500
    elif service in ["Anaesthesia"]:
        request.session['price'] = 10000
    elif service == "Anaesthesia and Critical Care Medicine":
        request.session['price'] = 20000
    
    price = request.session.get('price')
    print(f"{request.session['price']}")
    
    
    if request.method == 'POST':
        date_day_time = request.POST.get('date_day_time')
        date = date_day_time.split()[0]
        day = date_day_time.split()[1]
        time = " ".join(s for s in date_day_time.split()[2:])
        print(f"{date_day_time.split()} {date} {time}")

        if service != None:
            if date <= maxDate and date >= minDate:
                if day !="Friday" and day != "Sunday" :
                    if Appointment.objects.filter(service=service, day=date, time=time).count() < 1:
                        AppointmentForm = Appointment.objects.get_or_create(
                            service = service,
                            day = date,
                            time = time,
                            assigned_doctor = assigned_doctor,
                            uuid = user, 
                            price = price
                            )
                        validWorkdays.remove(date+' '+day+' '+time)
                        messages.success(request, "Appointment Saved!")
                        render(request, 'index.html',)
                    else:
                        messages.success(request, "The Selected Time Has Been Reserved Before!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                    print(f"{date}")
                    messages.success(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service!")
    
    return render(request, 'bookingSubmit.html', {
        'validWorkdays': validWorkdays,
        })


def userPanel(request):
    user = request.user
    print(f"{user} {bool(user.get_username())}")
    if not user.get_username():
        return render(request, 'index.html')
    
    name = user.name.split()
    first_name = name[0]
    last_name = name[-1]
    uuid = user.uuid
    role = ""
    image = None
    if user.account_type =="DOCTOR":
        role = Doctor.objects.get(persona_ptr_id=uuid).get_role_display()
        image = Doctor.objects.get(persona_ptr_id=uuid).image
        print(f"{image}")
    appointments = Appointment.objects.filter(uuid=uuid).order_by('app_id','day', 'time')
    
    """Debug line"""
    print(f"{appointments} {name}")
    
    return render(request, 'userPanel.html', {
        'user':user,
        'first_name': first_name,
        'last_name': last_name,
        'appointments':appointments,
        'role': role,
        'image': image,
        'media_root': settings.MEDIA_ROOT
    })

def userUpdate(request, app_id):
    sesh = request.POST
    print(f"SESH: {sesh}")            
            
    appointment = Appointment.objects.get(app_id__exact=app_id)
    userdatepicked = appointment.day
    service = appointment.service
    times = {}
    app_id = appointment.app_id
    #Copy  booking:
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')

    #24h if statement in template:
    delta24 = (userdatepicked).strftime('%Y-%m-%d') >= (today + timedelta(days=1)).strftime('%Y-%m-%d')
    #Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(22)

    #Only show the days that are not full:
    validWorkdays = isWeekdayValid(weekdays, service, times)

    #Store day and service in django session:
    request.session['service'] = service
    request.session['times'] = times
    request.session['validWorkdays'] = validWorkdays
    
    print(f"{service}...{validWorkdays}...{app_id}")
    

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        
        #Store day and service in django session:
        request.session['day'] = day
        request.session['service'] = service
        request.session['app_id'] = app_id

        print(f"{app_id}")
        
        return redirect('userUpdateSubmit', app_id=app_id)


    return render(request, 'userUpdate.html', {
            'weekdays':weekdays,
            'validWorkdays':validWorkdays,
            'delta24': delta24,
            'app_id': app_id,
        })

def userUpdateSubmit(request, app_id):
    user = request.user
    times = [
        "3 PM", "3:30 PM", "4 PM", "4:30 PM", "5 PM", "5:30 PM", "6 PM", "6:30 PM", "7 PM", "7:30 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    day = request.session.get('day')
    service = request.session.get('service')
    
    #Only show the time of the day that has not been selected before and the time he is editing:
    hour = checkEditTime(times, day, id)
    appointment = Appointment.objects.get(pk=id)
    userSelectedTime = appointment.time
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Saturday' or date == 'Wednesday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1 or userSelectedTime == time:
                            AppointmentForm = Appointment.objects.filter(pk=id).update(
                                user = user,
                                doctor_name = [],
                                service = service,
                                day = day,
                                time = time,
                                
                            ) 
                            messages.success(request, "Appointment Edited!")
                            return redirect('index')
                        else:
                            messages.success(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.success(request, "The Selected Day Is Full!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                    messages.success(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service!")
        return redirect('userPanel')


    return render(request, 'userUpdateSubmit.html', {
        'times':hour,
        'id': id,
    })

def staffPanel(request):
    user = request.user
    
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    
    #Only show the Appointments 21 days from today
    items = Appointment.objects.filter(day__range=[minDate, maxDate]).order_by('day', 'time')

    return render(request, 'staffPanel.html', {
        'items':items,
        "user": user,
        "name": user.name
    })
def getServices():
    services=[]
    for service in SERVICE_CHOICES:
        services.append(service[1])
    return services

def dayToWeekday(x):
    y = datetime.strptime(x, "%Y-%m-%d").strftime('%A')
    return y

def validWeekday(days):
    #Loop days you want in the next 21 days:
    today = datetime.now()
    weekdays = []
    for i in range (0, days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y not in ['Friday', 'Sunday']:
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays
    
def isWeekdayValid(x, service, times):
    validWorkdays = []
    for j in x:
        if datetime.strptime(j, '%Y-%m-%d').strftime('%A') in times.keys():
            if Appointment.objects.filter(day=j, service=service ).count() < len(times[datetime.strptime(j, '%Y-%m-%d').strftime('%A')]):
                for i in times[datetime.strptime(j, '%Y-%m-%d').strftime('%A')]:
                    if Appointment.objects.filter(day=j, service=service, time=i).count() < 1:
                        validWorkdays.append(f'{j} {datetime.strptime(j, "%Y-%m-%d").strftime("%A")} {i}')
    return validWorkdays

def checkEditTime(times, day, id):
    #Only show the time of the day that has not been selected before:
    x = []
    appointment = Appointment.objects.get(app_id=id)
    time = appointment.time
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1 or time == k:
            x.append(k)
    return x