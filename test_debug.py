import requests

# Simple bug example
code = """
def add(a, b):
    return a + b

result = add("5", 10)
"""

# Create debug request
debug_request = {
    "code": code,
    "error": "TypeError: can only concatenate str (not 'int') to str",
    "context": "Function is supposed to add two numbers"
}

# Make the request
response = requests.post(
    "http://localhost:8000/api/debug",
    json=debug_request
)

# Print response
print("\nStatus Code:", response.status_code)
print("\nResponse:")
try:
    print(response.json())
except:
    print(response.text)