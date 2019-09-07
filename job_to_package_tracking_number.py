"""
Load all (job number -> to job id) mappings givein in the import file
For every job, find all the packages currently in that job
Export a file with all (package tracking number -> job number) mappins
"""

import re
import requests
import api_utils as api
import file_utils as files
import utils

# EXPORT_FILEPATH = "/Users/mirek/job_mappings.tsv"
IMPORT_FILEPATH = "/Users/mirek/job_mappings_temp_2.tsv"

# EXPORT_FILEPATH = "/Users/mirek/package_to_job_mappings.tsv"
EXPORT_FILEPATH = "/Users/mirek/package_to_job_mappings_temp.tsv"

RUN_IN_PARALLEL = False # careful no to overwhelm the DB
ENVIRON = api.PROD

def main():
    print "Reading from file {}".format(IMPORT_FILEPATH)
    job_mapping_lines = files.get_lines(IMPORT_FILEPATH)

    print "Appending to file {}".format(EXPORT_FILEPATH)
    if RUN_IN_PARALLEL:
        utils.parallelize_with_param(get_and_write_packages_for_job, job_mapping_lines)
    else:
        for job_mapping_line in job_mapping_lines:
            get_and_write_packages_for_job(job_mapping_line)

def get_and_write_packages_for_job(job_mapping_line):
    [job_number, job_id] = job_mapping_line.split("\t")
    tracking_numbers = get_tracking_numbers(job_id)
    with open(EXPORT_FILEPATH, "a+") as f:
        for package in tracking_numbers:
            line_to_save = "{}\t{}\n".format(package, job_number)
            print line_to_save.replace("\n", "")
            f.write(line_to_save)

def get_tracking_numbers(job_id):
    raw_response = requests.get(
        "{}/Admin/Home/JobDetail?jobId={}".format(api.get_admin_dashboard_url(ENVIRON), job_id),
        headers=api.get_admin_dashboard_headers(ENVIRON),
        cookies=api.get_admin_dashboard_cookies(ENVIRON)
    )
    raw_response.raise_for_status()
    html = raw_response.text

    regex = r"/Admin/Home/PackageDetail/([A-Z0-9]+)\""
    matches = re.finditer(regex, html, re.MULTILINE)
    tracking_numbers = [match.group(1) for match in matches]

    return tracking_numbers


if __name__ == '__main__':
    main()
