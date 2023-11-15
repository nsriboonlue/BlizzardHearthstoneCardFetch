import requests
import json
import sys
from flask import Flask
from flask import render_template

app = Flask(__name__)

#Function for generating access token via OAUTH
def generate_token():
    auth_server_url = "https://oauth.battle.net/token"

    #Please insert your own client_id and client_secret
    client_id = '****************************'
    client_secret = '****************************'

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

#Bounded flask function to display Hearthstone cards at  "http://127.0.0.1:5000/hearthstone"
@app.route('/hearthstone')
def displayTenCards():

    #Generate Access token
    request_token = generate_token()

    #Base API URL and header
    base_url = "https://us.api.blizzard.com/hearthstone/cards/"
    head = {"Authorization": "Bearer " + request_token}

    #Looking to search for only 10 cards of the following criteria:
    # manaCost > 7 (Hearthstone API says value of 10 means 10 or greater),
    # Warlock or Druid class
    # Legendary rarity
    params = {
        "page": 1,
        "pageSize": 10,
        "locase": "en_US",
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
    json_response['cards'].sort(key=lambda p: p['id'], reverse=False)

    return render_template('index.html', title="page", jsonfile=json.dumps(json_response, indent=4))


if __name__ == '__main__':
    app.run()