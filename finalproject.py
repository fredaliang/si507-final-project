from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import requests
import webbrowser
import pprint as pp
import json
import matplotlib.pyplot as plt
import os
import sys

booking_hotel_url = 'https://www.booking.com/searchresults.en-us.html?ss=Tokyo&ssne=Tokyo&ssne_untouched=Tokyo&label=gen173nr-1FCAEoggI46AdIM1gEaJsCiAEBmAExuAEHyAEM2AEB6AEB-AECiAIBqAIDuAL1usyhBsACAdICJDE4MjU1NWY0LTdhY2MtNGZiMS04ZjQ1LWRhM2IzYmQ1NmU4YdgCBeACAQ&sid=66a94a2895c1433745f288f644b3115b&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=-246227&dest_type=city&checkin=2023-07-01&checkout=2023-07-07&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure'
google_api_key = None

def save_hotel_data(url):
    """
    Retrive the needed data of hotels from booking.com
    Convert the hotel data into a list of dictionaries
    Save the data into a json file

    Parameters:
    url (str): a url from booking.com with hotel search results

    Returns: None
    """
    # setup webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    # create an empty dict to store all hotel data
    hotels = []
    # create an empty dict to store all hotel data
    data = {}
    # scrap the needed hotel data
    property_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="property-card"]')
    for property in property_cards:
        data['name'] = property.find_element(By.CSS_SELECTOR,'div[data-testid="title"]').text
        data['address'] = property.find_element(By.CSS_SELECTOR,'[data-testid="address"]').text
        data['price'] = property.find_element(By.CSS_SELECTOR,'[data-testid="price-and-discounted-price"]').text
        data['url'] = property.find_element(By.CSS_SELECTOR,'a[data-testid="title-link"]').get_attribute('href')
        data['image'] = property.find_element(By.CSS_SELECTOR, '[data-testid="image"]').get_attribute('src')

        hotels.append(data)

    with open('hotels_data.json', 'w') as json_file:
        json.dump(hotels, json_file)

def create_hotel_tree(list_of_hotels):
    """
    Returns a dictionary of dictionaries of hotel data as a tree network
    The root node is 'Hotels' with each hotel data as its sub-node

    Parameters:
    list_of_hotels (list): a list of dictionaries of hotel data

    Return:
    tree (dictionary): a dictionary of dictionaries of hotel data
    """
    tree = {'Hotels': {}}
    for hotel_data in list_of_hotels:
        if hotel_data['name'] not in tree['Hotels'].keys():
            hotel_node = {
                'name': hotel_data['name'],
                'address': hotel_data['address'],
                'price': hotel_data['price'],
                'url': hotel_data['url'],
                'image': hotel_data['image']
            }
            tree['Hotels'][hotel_data['name']] = hotel_node

    return tree

def convert_price(price):
    """
    Convert price from string to a numeric value,
    and remove special character such as dollar sign and comma

    Parameters:
    price (str): price as a string value

    Returns only the float value of the price
    """
    return float(price.translate({ord(i): '' for i in '$,'}))
    # return float(price[1:].replace(',',''))

def get_fit_hotels(list_of_hotels, budget):
    """
    Returns a list of hotel names that fit the expected budget

    Parameters:
    list_of_hotels (list): a list of dictionaries of hotels
    budget (float): a numeric value representing the expected budget

    Returns:
    fit_hotels (list): a list of hotel names
    """
    fit_hotels = []
    for hotel in list_of_hotels:
        # for hotel in hotels:
        if convert_price(hotel['price']) <= budget:
            fit_hotels.append(hotel['name'])
    return fit_hotels

def save_google_review_data(hotel_name):
    """
    Retrive the needed data of hotel from Google Places API
    Convert the data into a dictionary
    Save the data into a json file

    Parameters:
    hotel_name (str): the hotel name to be searched

    Returns: None
    """

    url = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={hotel_name}&inputtype=textquery&fields=place_id,geometry&key={google_api_key}'
    response = requests.get(url)
    hotel = response.json()

    google_review_data = {}

    if hotel['status'] == 'OK':
        hotel_data = hotel['candidates'][0]
        place_id = hotel_data['place_id']
        location = f"{hotel_data['geometry']['location']['lat']},{hotel_data['geometry']['location']['lng']}"

        # Get place details, including reviews and rating
        place_details_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,review&key={google_api_key}'
        place_details_response = requests.get(place_details_url)
        place_details = place_details_response.json()

        name = place_details['result']['name']
        rating = place_details['result'].get('rating', 'No rating available')
        reviews = place_details['result'].get('reviews', [])

        google_review_data['name'] = name
        google_review_data['rating'] = rating
        google_review_data['reviews'] = []
        google_review_data['places'] = []

        if reviews:
            for review in reviews:
                author_name = review['author_name']
                review_text = review['text']
                review_rating = review['rating']
                google_review_data['reviews'].append([author_name, review_text, review_rating])
        else:
            print("Sorry, there is no review for now.")

        google_review_data['review_count'] = len(google_review_data['reviews'])

        radius = 500  # in meters
        nearby_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&key={google_api_key}'
        nearby_response = requests.get(nearby_url)
        nearby_places = nearby_response.json()

        for place in nearby_places['results']:
            place_name = place['name']
            place_rating = place.get('rating', 'No rating available')
            google_review_data['places'].append([place_name, place_rating])
    else:
        print("Sorry, the hotel is not found on Google map.")

    # return google_review_data
    with open('google_review_data.json', 'w') as json_file:
        json.dump(google_review_data, json_file)

def read_json(filename):
    """
    Returns the data by reading from a json file

    Parameters:
    filename (str): the name of the json file

    Returns:
    data (dict/list): the data reading from the json file
    """
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

def show_image(url):
    """
    Display an image based on the given url

    Parameters:
    url (str): the url of an image

    Returns: None
    """
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.show()

def main():
    # scrap hotel data and save to json file
    save_hotel_data(booking_hotel_url)
    # read hotels data from json
    hotels = read_json('hotels_data.json')
    # turn the hotel data into a tree network
    hotel_tree = create_hotel_tree(hotels)

    # total_pages = int(driver.find_element(By.CSS_SELECTOR, 'div[data-testid="pagination"]  li:last-child').text)
    # for current_page in range(total_pages):
    #     del driver.requests
    #     next_page_btn = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Next page")]')
    #     next_page_btn.click()
    #     driver.wait_for_request("/dml/graphql", timeout=5)

    print("Welcome to 2023 Tokyo Hotel Planning!\n")

    keep_search = True
    while keep_search:
        try:
            exp_budget = float(input("How much do you wanna spend in total(USD)? "))
        except:
            print("Invalid input, please enter a number.")
            continue

        # get a list of hotel names based on user input
        fit_hotels = get_fit_hotels(hotels, exp_budget)

        # go through the list of hotels
        if len(fit_hotels) == 0:
            print("Sorry, there is no available hotel that fits your requirement. Please adjust your expectation.")
            continue
        else:
            for hotel in fit_hotels:
                print(f"Nice! Here's what we found for you: {hotel}.\n")
                price = hotel_tree['Hotels'][hotel]['price']
                address = hotel_tree['Hotels'][hotel]['address']
                image = hotel_tree['Hotels'][hotel]['image']
                url = hotel_tree['Hotels'][hotel]['url']

                # display the hotel address and price information
                print(f"{hotel} is located in {address} and it costs {price}.\n")
                # display the hotel image
                show_image(image)
                break

        # get google review data on this hotel
        save_google_review_data(hotel)
        google_data = read_json('google_review_data.json')

        # prompt for next steps
        while True:
            next_step = input("Enter 1 if you want to learn more about the hotel reviews, 2 if you want to check its nearby places, 3 if you want to book this hotel, 4 if you want to start a new search, 5 if you want to quit. ")

            if next_step == '1': # show hotel reviews data
                rating = google_data['rating']
                review_count = google_data['review_count']
                reviews = google_data['reviews']

                print(f"The overall rating is {rating} from {review_count} reviews.\n")
                print("Here are some reviews from past customers.\n")

                all_ratings = []
                for review in reviews:
                    print(f"User: {review[0]}\nReview: {review[1]}\nRating:{review[2]}\n")
                    all_ratings.append(review[2])
                plt.hist(all_ratings, bins=5, edgecolor='black')
                plt.title(f'Rating Distribution of {hotel}')
                plt.xlabel('Rating')
                plt.ylabel('Frequency')
                plt.show()

            elif next_step == '2': # show nearby places data
                places = google_data['places']
                print("Here are some interesting places nearby the hotel we found!")
                # show the first five nearby places data
                for place in places[:5]:
                    print(f"{place[0]}\nRating: {place[1]}\n")

            elif next_step == '3': # open hotel web page
                webbrowser.open_new_tab(url)

            elif next_step == '4' or next_step == '5': # break the nested while loop
                break
            else:
                print("Invalid input, please enter a number between 1-4.")

        if next_step == '4': # go back to the original prompt
            # continue
            os.execv(sys.executable, ['python'] + sys.argv)
        elif next_step == '5': # break the outer loop and end program
            print("Thank you! Have a nice trip in Tokyo!")
            keep_search = False
            break

if __name__ == '__main__':
    main()




