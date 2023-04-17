# si507-final-project
- Author: Freda Liang
- Class: WN 2023 SI507
- Uniqname: yzliang

## Description
This project builds a Hotel Booking Recommendation System (specificallt choosing 1 - 7 July, 2023 in Tokyo, Japan as example to demonstrate) that helps users make smart travel and hotel booking decisions by displaying the information of hotels based on user input of budget, etc.

## Instructions
### To execute the program
- On line 17 in the py file for the google_api_key variable, please replace None with the google api key attached at the end of the final project submission file on canvas

### To interact with the program
1. Enter a valid number as hotel budget for all nights
2. After being displayed the suggested the number, enter any of the followings for further information/interaction
- 1: hotel reviews
- 2: nearby places
- 3: hotel page
- 4: New search
- 5: Quit and end the program

## Packages Used
- from selenium import webdriver
- from seleniumwire import webdriver
- from selenium.webdriver.chrome.service import Service
- from webdriver_manager.chrome import ChromeDriverManager
- from selenium.webdriver.common.by import By
- from PIL import Image
- from io import BytesIO
- requests
- webbrowser
- matplotlib.pyplot

## Data Structure
I created a tree in the format of a dictionary of dictionaries as the data structure for the hotel data retrieved from booking.com. Each hotel is the sub-node of the ‘Hotels’ root node. 

First, using the save_hotel_data() function, I retrieved the data fields (name, address, price, url, image) of the hotels into a list of dictionaries, and saved it into a json file.

Then, using the read_json() function, I read the data from the saved json file. 

With the create_hotel_tree() function, I created a tree structure of the hotels in a dictionary of dictionaries where each hotel is a sub-node of the ‘Hotels’ rootnode. And the data fields (name, address, price, url, image) are under each sub-node hotel too. 
