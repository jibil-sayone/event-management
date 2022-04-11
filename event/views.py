from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Q
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
import stripe


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
    if request.method == "POST":
        start_date = request.POST.get("start_date", None)
        end_date = request.POST.get("end_date", None)
        category = request.POST.get("category")
        key = request.POST.get("keyword")

        if start_date and end_date:
            filter_dict["end_date__date__range"] = [start_date, end_date]
        if category:
            filter_dict["categories"] = category
        if key:
            keyword_search = Q()
            keyword_search |= Q(title__icontains=key)
            keyword_search |= Q(description__icontains=key)
            events = Event.objects.filter(Q(**filter_dict) & Q(keyword_search)).order_by('start_date')
        else:
            events = Event.objects.filter(**filter_dict).order_by(
                'start_date')
    else:
        events = Event.objects.filter(**filter_dict).order_by('start_date')
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

    form = EventForm(instance=task)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'task':task,'form':form}

    return render(request, 'update_event.html', context)



def createEvent(request):

    form = EventForm()
    if request.user.is_authenticated:
        if request.method =='POST':
            form = EventForm(request.POST)
            if form.is_valid():
                form.save()
            return redirect('/')

    context = {'form':form}

    return render(request, 'add_event.html', context)


def PublishEvent(request, pk):
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
    success_url=YOUR_DOMAIN + '',
    cancel_url=YOUR_DOMAIN + '',
    )
    event = Event.objects.get(id=pk)
    event.paid = True
    event.published = True
    event.save()
    return redirect(checkout_session.url, code=303)


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
          payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event["type"] == 'checkout.session.completed':
        session = event["data"]["object"]

        if session.payment_status == 'paid':

            fullfill_order()

    return HttpResponse(status=200)

def fullfill_order():
    pass