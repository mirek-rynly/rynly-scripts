"""
Query the azure api to get the task / bug names for the given item numbers

Input: list of items (hardocded as "items" below)
Out: print list of items and descriptions
"""

from HTMLParser import HTMLParser
import re
import requests
import api_utils as api

html_parser = HTMLParser()

items = [283,302, 303, 315, 320,332, 336, 337, 338, 339, 341]
descriptions = []

for item in items:
    print "Fetching item {}".format(item)
    raw_response = requests.get(
        "{}/_workitems/edit/{}/".format(api.get_azure_devops_url(), item),
        headers=api.get_azure_devops_headers(),
        cookies=api.get_azure_devops_cookies(),
    )
    html_text = raw_response.text

    regex = r"<title>(?:Task|Bug) {}: (.+)</title>".format(item)
    matches = re.search(regex, html_text, re.MULTILINE)

    if matches:
        description = html_parser.unescape(matches.group(1))
        descriptions.append(description)
    else:
        print "Not match for the following regex:"
        print regex
        print "response was {}".format(raw_response)
        descriptions.append(None)

print "\nItems:"
print "\n".join(str(i) for i in items)

print "\nDescriptions:"
print "\n".join(descriptions)
