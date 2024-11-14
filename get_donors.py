import requests
from bs4 import BeautifulSoup
import json

# URL of the Matcherino contributions page
url = 'https://matcherino.com/tournaments/131953/contributions'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the JSON data within the script tag
    script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
    if script_tag:
        # Parse the JSON content from the script tag
        data = json.loads(script_tag.string)
        
        # Navigate to the transactions where donor information is stored
        transactions = data["props"]["pageProps"]["propdata"]["bounty"]["transactions"]
        
        # Prepare list to store donor data
        donors_list = []
        
        # Extract each donor's information
        for donation in transactions:
            name = donation.get("displayName", "Anonymous")
            amount = donation.get("amount", 0) / 100  # Assuming amount is in cents
            comment = donation.get("comment", "No comment")
            
            # Add the donor info to the list
            donors_list.append({
                "Donor": name,
                "Contribution": f"${amount:.2f}",
                "Comment": comment
            })
        
        # Save the donor data to a JSON file
        with open("get_donors.json", "w", encoding="utf-8") as f:
            json.dump(donors_list, f, ensure_ascii=False, indent=4)
        
        print("Donor data saved to get_donors.json.")
    else:
        print("Donor data not found in the page content.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
