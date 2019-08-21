import re
import requests
import api_utils as api

job_numbers = []
with open("/Users/mirek/competed_job_numbers.csv") as f:
    for line in f.read().splitlines():
        job_numbers.append(line)
print "Found {} job numbers".format(len(job_numbers))

for job_number in job_numbers:
    data = 'JobId={}&HubCode=&City=&Type=&DriverName=&Status=Completed&sortPagingModel%5BsortOrder%5D=JobCompleted_desc&sortPagingModel%5BcurrentPage%5D=1'.format(job_number)

    raw_response = requests.post(
        "{}/Admin/Home/FilterJobs".format(api.get_admin_dashboard_url(api.PROD)),
        data=data,
        headers=api.get_admin_dashboard_headers(api.PROD),
        cookies=api.get_admin_dashboard_cookies(api.PROD),
    )

    html = raw_response.text
    exp = r"GetJobDetailPopUp\('([\w\d-]*)'\)"
    regex_result = re.search(exp, html)
    if not regex_result:
        print "No result for job {}".format(job_number)
        print "Response: {}".format(raw_response)
        print
        print "HTML:"
        print html
        print
        continue

    package_id = regex_result.group(1)
    mapping_line = "{}\t{}".format(job_number, package_id)
    with open("/Users/mirek/job_mappings.tsv", "a+") as f:
        if mapping_line not in f.read().splitlines():
            print mapping_line
            f.write(mapping_line + "\n")
        else:
            print "Skipping {}".format(mapping_line)
