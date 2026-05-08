import requests

url = "https://backend-project2cp-2.onrender.com/api/users/forgot-password"
data = {"email": "oa_abid@esi.dz"}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
