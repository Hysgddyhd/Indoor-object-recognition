import requests
from typing import Dict, Any, Optional
import time

class Assistant:
    def __init__(self, token: str, base_url: str = 'https://kagi.com/api/v0/fastgpt'):
        """
        Initialize the Kagi API client.

        Args:
            token: Your Kagi API token
            base_url: Base URL for the API endpoint
        """
        self.base_url = base_url
        self.token = token
        self.request_count = 0
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bot {token}'})

    def make_request(self, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Make a request to the Kagi API.

        Args:
            query: The search query
            **kwargs: Additional parameters to include in the request

        Returns:
            Response JSON data or None if request fails
        """
        data = {"query": query}
        data.update(kwargs)

        try:
            response = self.session.post(self.base_url, json=data)
            response.raise_for_status()
            self.request_count += 1
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_request_count(self) -> int:
        """Get the total number of requests made."""
        return self.request_count

    def reset_request_count(self) -> None:
        """Reset the request counter to zero."""
        self.request_count = 0

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

# Usage example:
if __name__ == "__main__":
    # Replace with your actual token
    TOKEN = "ryjRZMT2ESfcWTFZdRGcLGD97crzU0bxfeK3zJpMmao.u-2quJGjWBFI6aXNdwTVJclx-PGmM8gvY-QerE_Kn4s"

    # Using context manager (recommended)
    with Assistant(TOKEN) as client:
        # Make requests
        result1 = client.make_request("python 3.11")
        result2 = client.make_request("machine learning basics")

        print(f"Response 1: {result1}")
        print(f"Response 2: {result2}")
        print(f"Total requests made: {client.get_request_count()}")

    # Or without context manager
    client = Assistant(token=TOKEN)
    result = client.make_request("artificial intelligence")
    print(f"Response: {result}")
    print(f"Request count: {client.get_request_count()}")
    client.close()
