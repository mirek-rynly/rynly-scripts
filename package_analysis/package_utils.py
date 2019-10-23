import os

ANALYSIS_FOLDER = os.path.abspath("/Users/mirek/Desktop/rynly_job_analysis")


# found packages with multiple pickup jobs (listed by both number and id) , igore the first one
# {'c6764abf-4805-427d-9cef-640fe3709333': ['3412', '3399'],'4c1d7752-445f-472e-9dc5-3728d59f7ec6': ['229', '228'], '9281c1a4-976e-4a10-b30b-016b53f79dce': ['156', '150'], '4349a36f-179c-4683-8866-b0a1de82124c': ['3228', '3226'], '24c43dcc-bdaa-49ea-968d-a1ead28d9266': ['1508', '1511']}
# {'c6764abf-4805-427d-9cef-640fe3709333': ['d821f6ab-b20e-4f99-aed4-b7f2f3448750', 'e1126c4f-89f5-488d-827f-0190d2a723b8'], '4c1d7752-445f-472e-9dc5-3728d59f7ec6': ['8ad32838-72c4-497c-a5d9-1a1afeed7c74', '5175468d-1d0c-46fa-813d-d6adb1ca65e9'], '9281c1a4-976e-4a10-b30b-016b53f79dce': ['8406f511-175a-4b63-a946-87561f358aa7', 'b4668184-56ee-488f-9924-b21e5e7740d4'], '4349a36f-179c-4683-8866-b0a1de82124c': ['3b1c37f4-7711-4b48-865d-fde4ae3d6c61', '0622f8f2-a97a-4e10-84c6-a29f9f555398'], '24c43dcc-bdaa-49ea-968d-a1ead28d9266': ['96b04795-99b8-48dd-b6ed-dbe7a3b0cd95', 'a96cebcf-d00b-4fee-83c9-92febe51624c']}
JOB_IDS_TO_IGNORE = set(["d821f6ab-b20e-4f99-aed4-b7f2f3448750", "8ad32838-72c4-497c-a5d9-1a1afeed7c74", "8406f511-175a-4b63-a946-87561f358aa7", "3b1c37f4-7711-4b48-865d-fde4ae3d6c61", "96b04795-99b8-48dd-b6ed-dbe7a3b0cd95"])


# input file format:
# _id,TrackingNumber,DateCreated,AmountPaid,JobId,IsExpedited,CancellationNote
def get_canceled_packages_set():
    cancelled_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "cancelled", "prod_cancelled_packages.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            cancelled_packages.add(_id)

    return cancelled_packages


# input file format:
# _id,Changes.0.Text,Changes.0.AdminChange,Changes.1.Text,Changes.1.AdminChange,Changes.2.Text,Changes.2.AdminChange,Changes.3.Text,Changes.3.AdminChange,Changes.4.Text,Changes.4.AdminChange,Changes.5.Text,Changes.5.AdminChange,Changes.6.Text,Changes.6.AdminChange,Changes.7.Text,Changes.7.AdminChangeChanges.8.Text,Changes.8.AdminChange,Changes.9.Text,Changes.9.AdminChange
def get_hub_dropoff_packages():
    hub_dropoff_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "package_changes", "package_changes.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            change_1 = line.split(",")[1]
            change_2 = line.split(",")[3]
            if change_1 == "Package Created" and change_2 == "Package Checked In":
                hub_dropoff_packages.add(_id)

    return hub_dropoff_packages


def get_admin_checked_in_packages():
    admin_checked_in_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "package_changes", "package_changes.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            change_2 = line.split(",")[3]
            change_2_is_admin = line.split(",")[4]
            if change_2 == "Package Picked By Driver" and change_2_is_admin == "true":
                admin_checked_in_packages.add(_id)

    # these jobs were created before we started tracking whether something was an admin change
    probably_admin_changes = ['859e7186-df59-4d29-afb9-026d34c9017f', '91508023-af37-46a8-a7cf-8e9ef27206db', 'b27ac951-3722-4909-876f-eb67a0d63b09', 'ab32a69b-8401-4928-a000-05374355621b', '9907ae2a-919e-4f85-93b5-7265dcf38c5a']
    admin_checked_in_packages.update(probably_admin_changes)

    return admin_checked_in_packages


def get_admin_delivered_packages():
    admin_delivered_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "package_changes", "package_changes.csv")) as f:
        header_line = f.readline()
        max_changes = int(header_line.split(".")[-2]) # user header to determine number of "changes" columns

        if header_line.split(",")[-1] != "Changes.{}.AdminChange\n".format(max_changes):
            raise Exception("Header format logic wrong")

        for line in f.read().splitlines():
            _id = line.split(",")[0]

            # find last package delivered change
            change_N_text = None
            change_N_is_admin = None
            for i in range(max_changes, -1, -1): # e.g. 9,8,...,0
                text_index = 2 * i + 1
                is_admin_index = 2 * i + 2

                change_N_text = line.split(",")[text_index]
                change_N_is_admin = line.split(",")[is_admin_index]

                if change_N_text == "Package Delivered":
                    break

            if not change_N_text:
                raise Exception("Package never got delivered?")

            if change_N_is_admin == "true":
                admin_delivered_packages.add(_id)

    return admin_delivered_packages

get_admin_delivered_packages()

# input file format:
# _id,HubId
def get_job_to_hub_id_map():
    job_to_hub_id = {}
    with open(os.path.join(ANALYSIS_FOLDER, "hubs", "prod_hubs_by_job.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            job_id = line.split(",")[0]
            hub_id = line.split(",")[1]
            job_to_hub_id[job_id] = hub_id

    return job_to_hub_id


# input file format:
# _id,TrackingNumber,DateCreated,AmountPaid,JobId,IsExpedited
def get_package_by_id_map(ignore_cancelled=True):
    package_by_id = {}
    cancelled_packages = get_canceled_packages_set() if ignore_cancelled else None
    with open(os.path.join(ANALYSIS_FOLDER, "prod_packages.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            if ignore_cancelled and _id in cancelled_packages:
                continue
            package_by_id[_id] = line

    return package_by_id

def get_job_id_from_package(package_by_id, p_id):
    return package_by_id[p_id].split(",")[4]

def get_package_qr_code(package_by_id, p_id):
    return package_by_id[p_id].split(",")[1]

def get_job_by_id_map():
    job_by_id = {}
    # _id,JobId,Type,TotalDistance,TrafficTotalTime,TrafficTotalDistance,TotalTime,ActualTotalTime,PayAmount,Shippers,DateCreated,DateCompleted,ContainsExpeditedPackage,
    with open(os.path.join(ANALYSIS_FOLDER, "prod_jobs.csv")) as f:
        for line in f.read().splitlines()[1:]:
            _id = line.split(",")[0]
            if _id in JOB_IDS_TO_IGNORE:
                continue
            job_by_id[_id] = line

    return job_by_id

def get_job_completed_date(job_by_id, j_id):
    return job_by_id[j_id].split(",")[11]

def get_job_number(job_by_id, j_id):
    return job_by_id[j_id].split(",")[1]

def get_shipper_and_nonshipper_job_sets(job_by_id_map, delivery_only=False):
    shipper_job_ids = set()
    nonshipper_job_ids = set()
    for job_id, job_line in job_by_id_map.iteritems():
        if "ShipperId" in job_line:
            shipper_job_ids.add(job_id)
            continue

        if not delivery_only or is_delivery_job(job_line):
            nonshipper_job_ids.add(job_id)

    return [shipper_job_ids, nonshipper_job_ids]

def is_delivery_job(job_line):
    return job_line.split(",")[2] == "1" # for Type, 0=pickup, 1=delivery

def get_job_cost(job_line):
    return int(job_line.split(",")[8])

# input file format:
# job_db_id,JobId,package_db_id
def get_package_to_jobs_and_job_to_packages(ignore_cancelled=True):
    package_to_job_ids = {}
    job_to_package_ids = {}
    cancelled_packages = get_canceled_packages_set() if ignore_cancelled else None
    with open(os.path.join(ANALYSIS_FOLDER, "prod_package_to_job_mapping.csv")) as f:
        for line in f.read().splitlines()[1:]:
            j_id = line.split(",")[0]
            p_id = line.split(",")[2]

            if j_id in JOB_IDS_TO_IGNORE:
                continue

            if ignore_cancelled and p_id in cancelled_packages:
                continue

            if p_id not in package_to_job_ids:
                package_to_job_ids[p_id] = []

            if j_id not in job_to_package_ids:
                job_to_package_ids[j_id] = []

            package_to_job_ids[p_id].append(j_id)
            job_to_package_ids[j_id].append(p_id)

    return [package_to_job_ids, job_to_package_ids]
