import requests

# Example debug session
debug_request = {
    "code": '''
def divide(a, b):
    return a / b
    ''',
    "error": "ZeroDivisionError: division by zero"
}

response = requests.post(
    "http://localhost:8000/debug",
    json=debug_request
)
print(response.json())