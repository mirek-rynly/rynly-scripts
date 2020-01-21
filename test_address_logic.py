import file_utils
import requests
import json

def main():

    API_KEY = "" # add your API key before running
    lines = file_utils.get_lines("/Users/mirek/Desktop/delivered_packages_addresses.csv")
    histogram = {}
    done = 0
    for line in lines[1:]: #skip header
        done += 1
        if done > 500:
            print "Finished"
            break

        entries = line.split(",")

        if "TB91849729SEA1" in entries: # has a "," in line2 field, just skip it
            continue

        [tracking_num, from_line_1, from_line_2, from_city, from_state, from_zip, from_coord_long_raw, from_coord_lat_raw, to_line_1, to_line_2, to_city, to_state, to_zip, to_coord_long_raw, to_coord_lat_raw] = entries
        # from_coord_lat = from_coord_lat_raw.replace('"','')
        # from_coord_long = from_coord_long_raw.replace('"','')
        # to_coord_lat = to_coord_long_raw.replace('"','')
        # to_coord_long = to_coord_long_raw.replace('"','')

        url_base = "https://maps.googleapis.com/maps/api/place/autocomplete/json?"
        params = "key={}&input={}, {}, {}".format(API_KEY, to_line_1, to_city, to_state)
        raw_response = requests.get(url_base + params)
        response = raw_response.json()

        place_id = response["predictions"][0]["place_id"]
        types = response["predictions"][0]["types"]
        for t in types:
            if t not in histogram:
                histogram[t] = 0
            histogram[t] += 1

        print "{}: {}".format(tracking_num, types)

    print "Results"
    print json.dumps(histogram, indent=1)


if __name__ == "__main__":
    main()
