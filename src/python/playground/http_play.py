import requests
url = 'https://httpbin.org/post'
data = {'key': 'value'}
response = requests.post(url, data=data)
print(response.status_code)
print(response.json())
"""
- `json=data` sets the `Content-Type` to `application/json`.
- `data=data` sets the `Content-Type` to `application/x-www-form-urlencoded`.
"""
