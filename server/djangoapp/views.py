from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from . import restapis
from .models import CarModel
# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)



# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)
    
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/djangoapp/')
        else:
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):    
    # print(request.user.username)
    logout(request)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')

        if User.objects.filter(username=username).exists():
            return render(request, 'djangoapp/registration.html', context)
        else:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            login(request, user)
            return redirect("djangoapp:index")  # 重定向到主页或其他适当页面
    else:
        return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
# def get_dealerships(request):
#     context = {}
#     url = "https://us-south.functions.appdomain.cloud/api/v1/web/05858487-77af-4822-a228-1a13c1a8254f/dealership-package/get-dealership"
    
#     # Call your function to get the list of dealerships
#     dealerships = restapis.get_dealers_from_cf(url)

#     # Add the dealerships to the context dictionary
#     context["dealership_list"] = dealerships
    
#     # Render the template with the context
#     return render(request, 'djangoapp/index.html', context)

def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/05858487-77af-4822-a228-1a13c1a8254f/dealership-package/get-dealership"
        dealerships = restapis.get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, "djangoapp/index.html", context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        # Get dealership details
        dealership_url = "https://us-south.functions.appdomain.cloud/api/v1/web/05858487-77af-4822-a228-1a13c1a8254f/dealership-package/get-dealership"
        dealership = restapis.get_dealer_by_id_from_cf(dealership_url, dealer_id)[0]
        context["dealership_details"] = dealership
        
        # Get all reviews of dealership
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/05858487-77af-4822-a228-1a13c1a8254f/dealership-package/get-review"
        reviews = restapis.get_dealer_reviews_from_cf(review_url, dealer_id)
        context["review_list"] = reviews
        
        return render(request, "djangoapp/dealer_details.html", context)
# ...
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    context = {}
    if request.user.is_authenticated is not True:
        return redirect("dealerships:dealer_details", dealer_id=dealer_id)
    
    dealership_url = "https://us-south.functions.appdomain.cloud/api/v1/web/05858487-77af-4822-a228-1a13c1a8254f/dealership-package/get-dealership"
    dealership = restapis.get_dealer_by_id_from_cf(dealership_url, dealer_id)[0]
    context["dealership_details"] = dealership
    if request.method == "POST":
        # Add new Review
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/05858487-77af-4822-a228-1a13c1a8254f/dealership-package/post-review"
        new_review= dict()
        new_review["dealership"] = dealer_id
        new_review["time"] = datetime.utcnow().isoformat()
        new_review["name"] = request.user.first_name + " " + request.user.last_name
        new_review["review"] = request.POST["content"]
        new_review["purchase"] = True if request.POST.get("purchasecheck") else False
        if new_review["purchase"]:
            new_review["purchase_date"] = request.POST.get("purchasedate")
            car_details = CarModel.objects.get(id=request.POST.get("car"))
            new_review["car_make"]= car_details.make.name
            new_review["car_model"]= car_details.name
            new_review["car_year"]= car_details.year.strftime("%Y")

        json_payload = dict()
        json_payload["review"] = new_review
        restapis.post_dealer_review(review_url, json_payload, dealerId=dealer_id)
        return redirect("dealerships:dealer_details", dealer_id=dealer_id)
    else:
        # Get cars for the dealer
        
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context["cars"] = cars
        return render(request, "djangoapp/add_review.html", context)

