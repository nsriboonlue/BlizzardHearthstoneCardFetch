import requests
import json
import sys
import os
from flask import Flask
from flask import render_template
from dotenv import load_dotenv

app = Flask(__name__)


#Function for generating access token via OAUTH
def generate_token():
    
    auth_server_url = "https://oauth.battle.net/token"

    #Load secrets from .env file
    load_dotenv()
    client_id = os.getenv('BLIZZARD_DEV_API_CLIENT_ID')
    client_secret = os.getenv('BLIZZARD_DEV_API_CLIENT_SECRET')

    token_req_payload = {'grant_type': 'client_credentials'}

    #Post to OAUTH server for access token
    token_response = requests.post(auth_server_url,
    data=token_req_payload, verify=False, allow_redirects=False,
    auth=(client_id, client_secret))

    #Exit code if the token request failed
    if token_response.status_code !=200:
        print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
        sys.exit(1)		    

    print("Successfuly obtained a new token")

    #Parse json return for access_token and returns it
    tokens = json.loads(token_response.text)
    
    return tokens['access_token']

#Send for MetaData request, and parse the data into Dictionaries.
def meta_data_request(request_token):

    set_dict = {}
    type_dict = {}
    class_dict = {}
    rarity_dict = {}

    #Base API URL and header
    base_url = "https://us.api.blizzard.com/hearthstone/metadata?locale=en_US"
    head = {"Authorization": "Bearer " + request_token}

    #Perform GET to the Hearthstone API
    response = requests.get(url=base_url, headers=head)

    #Exit code if GET fails
    if response.status_code != 200:
            print("Failed to fetch metadata from the hearthstone api", file=sys.stderr)
            sys.exit(1)	

    print("Successfuly fetched from Hearthstone API")
    json_response = json.loads(response.text)

    #Create type dictionary for HTML table parsing
    for type in json_response['types'] :
        type_dict[type['id']] = type['name']

    #Create set dictionary for HTML table parsing
    for set in json_response['sets'] :
        set_dict[set['id']] = set['name']
        
    #Create class dictionary for HTML table parsing
    for clas in json_response['classes'] :
        class_dict[clas['id']] = clas['name']

    #Create rarity dictionary for HTML table parsing
    for rare in json_response['rarities'] :
        rarity_dict[rare['id']] = rare['name']

    return set_dict, type_dict, class_dict, rarity_dict




#Bounded flask function to display Hearthstone cards at  "http://127.0.0.1:5000/hearthstone"
@app.route('/hearthstone')
def displayTenCards():

    #Generate Access token
    request_token = generate_token()

    #Send GET for MetaData and parse them into Dictionaries
    set_dict, type_dict, class_dict, rarity_dict = meta_data_request(request_token)

    #Base API URL and header
    base_url = "https://us.api.blizzard.com/hearthstone/cards/"
    head = {"Authorization": "Bearer " + request_token}

    #Looking to search for only 10 cards of the following criteria:
    # manaCost > 7 (Hearthstone API says value of 10 means 10 or greater),
    # Warlock or Druid class
    # Legendary rarity
    params = {
        "page": 2,
        "pageSize": 10,
        "locale": "en_US",
        "manaCost": "7,8,9,10",
        "class": "druid,warlock",
        "rarity": "legendary"
    }

    #Perform GET to the Hearthstone API
    response = requests.get(url=base_url, headers=head, params=params)

    #Exit code if GET fails
    if response.status_code != 200:
            print("Failed to fetch card from the hearthstone api", file=sys.stderr)
            sys.exit(1)		 
    


    #If successfully fetched the card data from API, render the HTML template
    print("Successfuly fetched from Hearthstone API")
    json_response = json.loads(response.text)

    with open('blizzdump.txt', 'w') as f:
        f.write(json.dumps(json_response, indent=4))

    #Parse json return with only what we need and then convert the ID's to the matching name from MetaData
    cardList = []
    for card in json_response['cards']:
        tempOutput = {}
        tempOutput['id']           = card['id']
        tempOutput['image']        = card['image']
        tempOutput['name']         = card['name']

        if(card['cardTypeId'] in type_dict ):
            tempOutput['cardTypeId']   = type_dict [   card['cardTypeId'] ]
        else :
            tempOutput['cardTypeId']    ="Card Type Not Found In MetaData: " + str(card['cardTypeId'])
        
        if(card['rarityId'] in rarity_dict ):
            tempOutput['rarityId']   = rarity_dict [   card['rarityId'] ]
        else :
            tempOutput['rarityId']    ="Rarity Type Not Found In MetaData: " + str(card['rarityId'])

        if(card['cardSetId'] in set_dict ):
            tempOutput['cardSetId']    = set_dict[ card['cardSetId'] ]
        else :
            tempOutput['cardSetId']    ="Set Not Found In MetaData: " + str(card['cardSetId'])

        if(card['classId'] in class_dict ):
            tempOutput['classId']    = class_dict[ card['classId'] ]
        else :
            tempOutput['classId']    ="Class Id Not Found In MetaData: " + str(card['classId'])
        cardList.append(tempOutput)

    #sort result by ID
    cardList.sort(key=lambda p: p['id'])

    return render_template('index.html', title="page", cards=cardList)


if __name__ == '__main__':

    app.run()
