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
#_id,TrackingNumber,DateCreated,AmountPaid,JobId,IsExpedited
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
    with open(os.path.join(ANALYSIS_FOLDER, "prod_jobs.csv")) as f_j:
        for line in f_j.read().splitlines()[1:]:
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
    with open(os.path.join(ANALYSIS_FOLDER, "prod_package_to_job_mapping.csv")) as f_ptj:
        for line in f_ptj.read().splitlines()[1:]:
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
