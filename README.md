# BlizzardTakeHomeCode  
Blizzard Take-Home assignment for SRE hiring process  

## Run instruction:    
-Clone code and update .env with your Blizzard Dev credentials    
-run pip install -requirements.txt  (should just need flask, requests, and dotenv)  
-python3 BlizzCodingAssignment.py    
-Open browser to "http://127.0.0.1:5000/hearthstone"    

## Requirements:  
    1. Create a web application to render requested information from the API into a human readable page.  
    2. Retrieve details of any 10 cards with the following criteria:  
        - Class: Druid or Warlock  
        - Mana: At least 7  
        - Rarity: Legendary  
    3. Display results must be sorted by card ID in a human readable table that includes:  
        - Card Image  
        - Name  
        - Type  
        - Rarity  
        - Set  
        - Class  

## Implementation:  
    1. Send POST requesting for access token to https://oauth.battle.net/token    
    2. Use the access token to send GET request to https://us.api.blizzard.com/hearthstone/metadata?locale=en_US for the Meta data  
    3. Parse the meta data into dictionaries  
    4. Use the access token to send GET request to https://us.api.blizzard.com/hearthstone/cards/ with the following params:    
        -params = {  
          "page": 1,  
          "pageSize": 10,  
          "locase": "en_US",  
          "manaCost": "7,8,9,10",  
          "class": "druid,warlock",  
          "rarity": "legendary"  
          }    
    5. Extract the needed data while mapping the individual ID's to their string equivalent from Meta data  
    6. Sort result by ID    
    7. Output result to Web Application at http://127.0.0.1:5000/hearthstone via Flask    
