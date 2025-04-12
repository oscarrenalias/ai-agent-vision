import requests

"""
1. Make web search: https://www.k-ruoka.fi/haku?q=jauheliha
2. Get value of cf_clearance and session cookies in response
3. Get value of every other cookie in response
4. Call JSON API with right cf_clearance and session cookies, as well as remaining cookies: https://www.k-ruoka.fi/kr-api/v2/product-search/jauheliha?storeId=N106&offset=0&limit=100

Note: this does not seem to work as either Cloudflare or K-Ruoka has a protection against scraping, and requesting from certain locations
will trigger a CAPTCHA request. I'm leaving this here for now for historical reasons, but it's probably not worth trying to defeat their
CAPTCHA.
"""


def search_k_ruoka(query):
    # Step 1: Make web search
    search_url = f"https://www.k-ruoka.fi/haku?q={query}"  # noqa: E231
    session = requests.Session()
    response = session.get(search_url)
    # Check if the response is successful
    if response.status_code != 200:
        # print request, response and cookies to stdout for inspection
        print("Request URL: ", search_url)
        print("Response Headers: ", response.headers)
        print("Response: ", response.text)
        print("Cookies: ", session.cookies.get_dict())

    response.raise_for_status()

    # Step 2: Get value of cf_clearance and session cookies in response
    cookies = session.cookies.get_dict()
    cf_clearance = cookies.get("cf_clearance")
    session_cookie = cookies.get("session")

    if not cf_clearance or not session_cookie:
        raise ValueError("Required cookies not found in the response")

    # Step 3: Get value of every other cookie in response
    other_cookies = {key: value for key, value in cookies.items() if key not in ["cf_clearance", "session"]}

    # Step 4: Call JSON API with the right cookies
    api_url = f"https://www.k-ruoka.fi/kr-api/v2/product-search/{query}?storeId=N106&offset=0&limit=100"  # noqa: E231
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    api_cookies = {"cf_clearance": cf_clearance, "session": session_cookie, **other_cookies}
    api_response = session.get(api_url, headers=headers, cookies=api_cookies)

    # Check if the API response is successful
    if api_response.status_code != 200:
        # print request, response and cookies to stdout for inspection
        print("Request URL:", search_url)
        print("Response Headers:", response.headers)
        print("Response:", response.text)
        print("Cookies:", cookies)

    api_response.raise_for_status()

    return api_response.json()


# Example usage
if __name__ == "__main__":
    query = "jauheliha"
    try:
        results = search_k_ruoka(query)
        print(results)
    except Exception as e:
        print(f"Error: {e}")
