import api_config as config

# Enums representing production vs UAT
PROD = "PROD"
UAT = "UAT"

def get_url(environ):
    url = {
        UAT: "https://uatuser.rynly.com",
        PROD: "https://user.rynly.com"
    }
    return url[environ]

def get_user_portal_cookies(environ):
    cookies = {
        UAT: config.USER_PORTAL_UAT_COOKIES,
        PROD: config.USER_PORTAL_PROD_COOKIES
    }
    return cookies[environ]

def get_user_portal_headers(environ):
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,cs;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": get_url(environ),
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
