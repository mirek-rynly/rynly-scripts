import re
import requests
import rynly_api_utils as api

job_id = "2f80711a-daf8-42f7-befc-18d1346a2c1e"
raw_response = requests.get(
    "{}/Admin/Home/JobDetail?jobId={}".format(api.get_admin_dashboard_url(api.PROD), job_id),
    headers=api.get_admin_dashboard_headers(api.PROD),
    cookies=api.get_admin_dashboard_cookies(api.PROD)
)

print raw_response
html = raw_response.text

regex = r"/Admin/Home/PackageDetail/([A-Z0-9]+)\""


matches = re.finditer(regex, html, re.MULTILINE)
for matchNum, match in enumerate(matches):
    print "{} {}".format(matchNum, match.group(1))
exit(0)

