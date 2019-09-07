"""
Get a mapping of [job number] -> [job object ID] for jobs in the given range
Append the data to the given tsv file
"""

import re
import requests
import api_utils as api

# job_numbers = files.get_lines("/Users/mirek/competed_job_numbers.csv")
# print "Found {} job numbers".format(len(job_numbers))

# EXPORT_FILEAPTH = "/Users/mirek/job_mappings.tsv"
EXPORT_FILEAPTH = "/Users/mirek/job_mappings_temp_2.tsv"

# Code also has a "ReadyToStart" enum?
# different order than code: compelted is first for early exit
# ignore ready to open, we don't use it atm
JOB_STATUSES = ["Completed", "Pending", "Open", "Assigned", "Started"] #, "ReadyToOpen"]

job_numbers = range(3250, 3348)

def main(environ=api.PROD):
    for job_number in job_numbers:

        job_id = get_job_id(job_number, environ)
        if not job_id:
            print "Failed to find job {}".format(job_number)
            continue

        mapping_line = "{}\t{}".format(job_number, job_id)
        with open(EXPORT_FILEAPTH, "a+") as f:
            print mapping_line
            f.write(mapping_line + "\n")

    print "DONE"

def get_job_id(job_number, environ):
    print "Searching for job {}".format(job_number)
    for job_status in JOB_STATUSES:
        data = get_data_payload(job_number, job_status)

        raw_response = requests.post(
            "{}/Admin/Home/FilterJobs".format(api.get_admin_dashboard_url(environ)),
            data=data,
            headers=api.get_admin_dashboard_headers(environ),
            cookies=api.get_admin_dashboard_cookies(environ),
        )

        html = raw_response.text
        exp = r"GetJobDetailPopUp\('([\w\d-]*)'\)"
        regex_result = re.search(exp, html)
        if regex_result:
            return regex_result.group(1)

        print "No result for status '{}', response was {}".format(job_status, raw_response)

    return None


def get_data_payload(job_number, job_status):
    if job_status not in JOB_STATUSES:
        raise Exception("'{}' isn't a valid job status".format(job_status))

    sort_order = "JobCompleted_desc" if job_status == "Completed" else "CurrentState"
    return 'JobId={}&HubCode=&City=&Type=&DriverName=&Status={}&sortPagingModel%5BsortOrder%5D={}&sortPagingModel%5BcurrentPage%5D=1'.format(job_number, job_status, sort_order)

if __name__ == '__main__':
    main()
