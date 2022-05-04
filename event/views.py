from django.shortcuts import render,redirect
from django.http import Http404
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
import stripe
from django.contrib import messages

# Create your views here.

stripe.api_key = 'sk_test_51KGQMoSHH8WqtIRyo6XGgOPRlC0HO7G8lvnFAb1CtPymhUjUOrCGDUSiDqCw5dZValm5FeOyduM0KAsXyVkqy27C00B4S7SURw'
endpoint_secret = "whsec_jgZliM2H6ycKmBzvttqVgNr3USAsFXpA"
YOUR_DOMAIN = 'http://localhost:8000'


def index(request):
    """
    Returns the list event to show users
    """
    filter_dict = {}
    filter_dict["end_date__date__gte"] = datetime.today().date()
    filter_cat = Event.objects.values("categories").distinct()
    if request.user.is_authenticated:
        events = Event.objects.filter(**filter_dict).order_by('start_date')
    else:
        events = Event.objects.filter(**filter_dict).filter(published="True").order_by('start_date')
    page = request.GET.get('page', 1)
    paginator = Paginator(events, 10)
    try:
        eventlist = paginator.page(page)
    except PageNotAnInteger:
        eventlist = paginator.page(1)
    except EmptyPage:
        eventlist = paginator.page(paginator.num_pages)

    return render(request, 'events.html', {'events': eventlist, 'category': filter_cat})

def updateEvent(request, pk):

    task = Event.objects.get(id=pk)

    if not request.user.is_authenticated:

        return redirect(YOUR_DOMAIN + '/login/')

    elif task.created_by != request.user:

        return render(request, 'not_found.html')

    else:

        form = EventForm(instance=task)

        if request.method == 'POST':
            form = EventForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                messages.success(request, "Event Updated Successfully")
                return redirect('/')

        context = {'task':task,'form':form}

        return render(request, 'update_event.html', context)



def createEvent(request):

    if not request.user.is_authenticated:
        return redirect(YOUR_DOMAIN + '/login/')
    else:
        form = EventForm()
        if request.method =='POST':
            form = EventForm(request.POST)
            if form.is_valid():
                new_event = form.save()
                new_event.created_by = request.user
                new_event.save()
                messages.success(request, "New Event Added Successfully")
                return redirect('/')

        context = {'form':form}

        return render(request, 'add_event.html', context)



def PublishEvent(request, pk):

    if not request.user.is_authenticated:
        return redirect(YOUR_DOMAIN + '/login/')
    else:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': 'Events',
                    },
                    'unit_amount': 2000,
                },
                'quantity': 1,
            }],
        mode='payment',
        success_url=YOUR_DOMAIN + '/pay_success/{0}'.format(pk),
        cancel_url=YOUR_DOMAIN + '/pay_fail/',
        )
        return redirect(checkout_session.url, code=303)


def fullfill_order(request,pk):

    if not request.user.is_authenticated:
        return redirect(YOUR_DOMAIN + '/login/')
    else:
        event = Event.objects.get(id=pk)
        event.paid = True
        event.published = True
        event.save()
        messages.success(request, "Your Event is successfully published")
        return redirect(YOUR_DOMAIN + '')

def cancel_order(request):

    if not request.user.is_authenticated:
        return redirect(YOUR_DOMAIN + '/login/')
    else:
        messages.success(request, "Your operation is failed Please Try Again")
        return redirect(YOUR_DOMAIN + '')