import requests

# Replace 'secret_api_key' with your actual SerpApi API key
api_key = 'aeca1c4aeae121e4f042ee6cf9f93b6d1846304f2b91f6f325c4b115f853ca78'

# Set up the endpoint and parameters
endpoint = 'https://serpapi.com/search'
params = {
    'q': 'where is puttur',
    'location': 'Karnataka, India',
    'hl': 'en',
    'gl': 'us',
    'google_domain': 'google.com',
    'api_key': api_key
}


# Make the GET request
response = requests.get(endpoint, params=params)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON response
    results = response.json()

    # Extract and print the concise answer from the answer box
    if 'answer_box' in results:
        answer = results['answer_box']['answer']
        print(f"Concise answer: {answer}")
    else:
        # If no concise answer found, try to extract the top result
        if 'organic_results' in results and len(results['organic_results']) > 0:
            top_result = results['organic_results'][0]
            title = top_result.get('title', 'No title found')
            link = top_result.get('link', 'No link found')
            print(f"Top result: {title} - {link}")
        else:
            print("No relevant result found.")
else:
    print(f"Error: {response.status_code}, {response.text}")