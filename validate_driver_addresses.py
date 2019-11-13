"""
Run address validation to backfill driver address coordinates.

Query to export local copy of Users collection
mongoexport -u rynlyproduction -p`cat ~/.ssh/rynly_cosmosdb_production` -h rynlyproduction.documents.azure.com:10255 -d rynlyproduction -c Users --ssl > Users_2019_11_12.js

Query to create input driver_address.csv:
mongoexport --db rynly_users_2019_11_12 --collection Users --type=csv --fields _id,FirstName,LastName,Email,Address.Line1,Address.City,Address.State,Address.Zip,Address.Location.coordinates.0,Address.Location.coordinates.0 -q '{"UserType": "Driver", "PaymentInfoAdded": true}' > driver_addresses.csv

Make sure to remove all inner-cell commas (as well as the surrounding quotes serving as escape chars)

"""

import requests
import file_utils
import api_utils as api


def main(environ=api.UAT):

    failed_lines = []
    fixed_lines = []
    all_lines = file_utils.get_lines("/Users/mirek/driver_addresses.csv")
    for address_str in all_lines[1:]: #skip header
        print address_str

        address_line = address_str.split(",")
        recommended_address = get_recommended_address(environ, address_line)
        if not recommended_address:
            failed_lines.append(address_line)
        else:
            location = recommended_address["location"]
            fixed_line = address_line + [str(location["latitude"]), str(location["longitude"])]
            fixed_lines.append(fixed_line)

    print "exporting {} failed and {} fixed lines".format(len(failed_lines), len(fixed_lines))

    orig_header_str = all_lines[0]
    fixed_header_str = orig_header_str + ",new_latitude,new_longitude"
    export_lines(failed_lines, "/Users/mirek/Desktop/failed_driver_addresses.csv", orig_header_str)
    export_lines(fixed_lines, "/Users/mirek/Desktop/fixed_driver_addresses.csv", fixed_header_str)


def export_lines(lines, file_path, header_str):
    with open(file_path, "w") as f:
        f.write(header_str + "\n")
        for line in lines:
            f.write(",".join(line) + "\n")


def get_recommended_address(environ, address_line):
    [_id, first_name, last_name, email, address, city, state, zip_code, o_lat, o_lon] = address_line
    address_payload = {
        "city": city,
        "line1": address,
        "state": state,
        "zip": zip_code
    }

    validation_url = "{}/api/hub/validateAddress".format(api.get_user_portal_url(environ))
    headers = api.get_user_portal_headers(environ)
    cookies = api.get_user_portal_cookies(environ)

    raw_response = requests.post(validation_url, json=address_payload, headers=headers, cookies=cookies)
    response = raw_response.json()

    if response["hasError"]:
        print "\tErrors: {}".format(response["errors"])
        return None

    data = raw_response.json()["data"]
    return data["recommendedAddress"]


if __name__ == "__main__":
    main()
