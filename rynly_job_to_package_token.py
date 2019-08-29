import re
import requests
import api_utils as api
import file_utils as files
import utils

# EXPORT_FILEPATH = "/Users/mirek/job_mappings.tsv"
IMPORT_FILEPATH = "/Users/mirek/job_mappings_temp.tsv"

# EXPORT_FILEPATH = "/Users/mirek/package_to_job_mappings.tsv"
EXPORT_FILEPATH = "/Users/mirek/package_to_job_mappings_temp.tsv"

RUN_IN_PARALLEL = False
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
    [job_number, job_hash] = job_mapping_line.split("\t")
    raw_response = requests.get(
        "{}/Admin/Home/JobDetail?jobId={}".format(api.get_admin_dashboard_url(ENVIRON), job_hash),
        headers=api.get_admin_dashboard_headers(ENVIRON),
        cookies=api.get_admin_dashboard_cookies(ENVIRON)
    )
    raw_response.raise_for_status()
    html = raw_response.text

    regex = r"/Admin/Home/PackageDetail/([A-Z0-9]+)\""
    packages = [match.group(1) for match in re.finditer(regex, html, re.MULTILINE)]

    with open(EXPORT_FILEPATH, "a+") as f:
        for package in packages:
            line_to_save = "{}\t{}\n".format(package, job_number)
            print line_to_save.replace("\n", "")
            f.write(line_to_save)


if __name__ == '__main__':
    main()
