def sanitize_input(text: str) -> str:
    return text.strip()

def format_error_message(error: Exception) -> str:
    return f"{type(error).__name__}: {str(error)}