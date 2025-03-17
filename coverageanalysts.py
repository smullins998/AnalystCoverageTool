import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
import json  # Add this import at the top
# Replace with your actual API token
API_TOKEN = "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"

# API endpoint
url = "https://api.perplexity.ai/chat/completions"

# Headers including the authorization token
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}


df = pd.read_excel('Manufacturing.xlsx')

company_list = []
firm_list = []
analyst_list = []


for organization_name in tqdm(df['Account Name']):
    
    try:

    

        prompt = f"""
    Search for "{organization_name} investor relations analyst coverage" and find the official IR webpage that lists their coverage analysts.

    Focus specifically on pages with URLs like:
    - "{organization_name}.com/investor/analyst-coverage"
    - "{organization_name}.com/investors/analyst-coverage" 
    - "{organization_name}.com/ir/analyst-coverage"
    - "ir.{organization_name}.com/analyst-coverage"
    - "investors.{organization_name}.com/analyst-coverage"

    Extract ONLY the analysts directly listed on the company's official IR page.

    Return the results in JSON format exactly matching this schema:

    "company": "{organization_name}",
    "coverage_analysts": 
        
        "firm": "Firm Name",
        "analyst": "Analyst Name"
        
        
        "firm": "Firm Name",
        "analyst": "Analyst Name"
        
    


    If no official IR page with analyst coverage is found, return an empty array for coverage_analysts.
    Return only the JSON response, no additional text.

    """


        # Define the payload (body) of the request
        payload = {
            "model": "sonar-pro",  # Replace with the model you want to use
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "search_domain_filter": ["perplexity.ai"],  # Optional: Filter search domains
            "return_images": False,  # Optional: Set to True if you want images
            "return_related_questions": False,  # Optional: Set to True if you want related questions
            "stream": False,  # Optional: Set to True for streaming responses

        }



        # Send the POST request to the API
        
        response = requests.post(url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            response_json = response.json()
            
            # Extract the assistant's reply
            assistant_reply = response_json['choices'][0]['message']['content']
            # print("Assistant's Reply:", assistant_reply)
            
            # Optionally, print citations if available
            # if 'citations' in response_json:
            #     print("Citations:", response_json['citations'])
                
            assistant_reply = json.loads(assistant_reply)
            
            for firm in assistant_reply['coverage_analysts']:
                if firm['analyst'] != '':
                    firm_list.append(firm['firm'])
                    analyst_list.append(firm['analyst'])
                    company_list.append(organization_name)
                
                

        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(e)
        continue
            

df = pd.DataFrame({'company': company_list, 'firm': firm_list, 'analyst': analyst_list})
df.to_excel('coverage_analysts.xlsx', index=False)






