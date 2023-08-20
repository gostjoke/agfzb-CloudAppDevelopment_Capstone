import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


def get_request(url, **kwargs):
    print(kwargs)
    try:
        if "apikey" in kwargs:
            response = requests.get(url, headers={
                                    'Content-Type': 'application/json'}, params=kwargs, auth=HTTPBasicAuth("apikey", kwargs["apikey"]))
        else:
            response = requests.get(
                url, headers={'Content-Type': 'application/json'}, params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
    except Exception as e:
        print("Error ", e)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def post_request(url, json_payload, **kwargs):
    # print(json_payload)
    # print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        print(json_data)
        return json_data
    except:
        print("Network exception occurred")


def get_dealers_from_cf(url, **kwargs):
    results = []
    # - Call get_request() with specified arguments
    json_result = get_request(url)
    # - Parse JSON results into a CarDealer object list
    if json_result:
        dealerships = json_result
        for dealer in dealerships:
            dealer_details = dealer['doc']
            dealer_obj = CarDealer(
                address=dealer_details['address'],
                city=dealer_details['city'],
                full_name=dealer_details['full_name'],
                id=dealer_details['id'],
                lat=dealer_details['lat'],
                long=dealer_details['long'],
                short_name=dealer_details['short_name'],
                st=dealer_details['st'],
                zip=dealer_details['zip'],
            )
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # - Call get_request() with specified arguments
    json_result = get_request(url, dealerId=dealerId)
    # print(json_result)
    if json_result:
        dealer_reviews = json_result
        for review in dealer_reviews:
            print(review)
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                # id=review["_id"],
                review=review["review"],
                purchase=review["purchase"],
                purchase_date= review.get("purchase_date") if review.get("purchase_date") else '',
                car_make=review.get("car_make") if review.get("car_make") else '',
                car_model=review.get("car_model") if review.get("car_model") else '',
                car_year=review.get("car_year") if review.get("car_year") else '',
                sentiment=''
            )
            # review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
    return results


def post_dealer_review(url, payload, **params):
    # - Call get_request() with specified arguments
    json_result = post_request(url, payload, **params)
    
    return json_result


def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # - Call get_request() with specified arguments
    json_result = get_request(url, dealerId=dealerId)
    # - Parse JSON results into a CarDealer object list
    if json_result:
        dealerships = json_result
        for dealer_details in dealerships:
            dealer_obj = CarDealer(
                address=dealer_details['address'],
                city=dealer_details['city'],
                full_name=dealer_details['full_name'],
                id=dealer_details['id'],
                lat=dealer_details['lat'],
                long=dealer_details['long'],
                short_name=dealer_details['short_name'],
                st=dealer_details['st'],
                zip=dealer_details['zip'],
            )
            results.append(dealer_obj)
    return results

def get_dealer_by_state_from_cf(url, state):
    results = []
    # - Call get_request() with specified arguments
    json_result = get_request(url, state=state)
    # - Parse JSON results into a CarDealer object list
    if json_result:
        dealerships = json_result
        for dealer_details in dealerships:
            dealer_obj = CarDealer(
                address=dealer_details['address'],
                city=dealer_details['city'],
                full_name=dealer_details['full_name'],
                id=dealer_details['id'],
                lat=dealer_details['lat'],
                long=dealer_details['long'],
                short_name=dealer_details['short_name'],
                st=dealer_details['st'],
                zip=dealer_details['zip'],
            )
            results.append(dealer_obj)
    return results


"""
# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    url = os.getenv('IBM_WATSON_NLU_API_URL')

    api_key = os.getenv('IBM_WATSON_NLU_API_KEY')

    authenticator = IAMAuthenticator(api_key) 

    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 

    natural_language_understanding.set_service_url(url) 
    try:
        response = natural_language_understanding.analyze( text=text ,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result()

    except:
        return ('could not evaluate')

    label=json.dumps(response, indent=2) 

    # - Get the returned sentiment label such as Positive or Negative
    label = response['sentiment']['document']['label'] 

    return (label) 
"""

def analyze_review_sentiments(dealer_review):
    API_KEY = ""
    NLU_URL = 'https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/351966a8-a214-4fc1-a319-ea7f066c002c'
    authenticator = IAMAuthenticator(API_KEY)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01', authenticator=authenticator)
    natural_language_understanding.set_service_url(NLU_URL)
    response = natural_language_understanding.analyze(text=dealer_review, features=Features(
        sentiment=SentimentOptions(targets=[dealer_review]))).get_result()
    label = json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    return(label)