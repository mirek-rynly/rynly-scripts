import api_config as config

# Enums representing production vs UAT
PROD = "PROD"
UAT = "UAT"


############# USER PORTAL #############

def get_user_portal_url(environ):
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
        "Origin": get_user_portal_url(environ),
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }


############# ADMIN DASHBOARD #############

def get_admin_dashboard_url(environ):
    url = {
        UAT: "https://uatdashboarduser.rynly.com",
        PROD: "https://dashboard.rynly.com"
    }
    return url[environ]

def get_admin_dashboard_cookies(environ):
    cookies = {
        UAT: config.ADMIN_DASHBOARD_UAT_COOKIES,
        PROD: config.ADMIN_DASHBOARD_PROD_COOKIES
    }
    return cookies[environ]

def get_admin_dashboard_headers(environ):
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,cs;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": get_user_portal_url(environ),
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }


############# AZURE DEVOPS #############

def get_azure_devops_url():
    return "https://dev.azure.com/rynly/Rynly"

def get_azure_devops_cookies():
    return config.AZURE_DEVOPS_COOKIES

def get_azure_devops_headers():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,cs;q=0.8",
        "authority": "dev.azure.com",
        "cache-control": "max-age=0",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }


