import requests

url = "http://localhost:8000/api/v1/farms/create"

# First, need to get a token
login_url = "http://localhost:8000/api/v1/auth/signin"
login_response = requests.post(login_url, json={"username": "puneetxp", "password": "Password1!"})

if login_response.status_code != 200:
    print("Login failed:", login_response.text)
else:
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "name": "Green Valley Farm",
        "state": "Haryana",
        "district": "Gurugram",
        "village": "Test Village",
        "pincode": "122001",
        "address_line": "Plot 45, Sector 12, Near NH-8",
        "total_area_acres": 5.5,
        "latitude": 28.4595,
        "longitude": 77.0266,
        "plots": [
            {
                "name": "Main Plot - Green Valley Farm",
                "area_acres": 2.8
            }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
