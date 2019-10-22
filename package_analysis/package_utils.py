import os

ANALYSIS_FOLDER = os.path.abspath("/Users/mirek/Desktop/rynly_job_analysis")

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


def get_job_by_id_map():
    job_by_id = {}

    print "READING PROD JOBS FILE"
    # _id,JobId,Type,TotalDistance,TrafficTotalTime,TrafficTotalDistance,TotalTime,ActualTotalTime,PayAmount,Shippers,DateCreated,DateCompleted,ContainsExpeditedPackage,
    with open(os.path.join(ANALYSIS_FOLDER, "prod_jobs.csv")) as f_j:
        for line in f_j.read().splitlines()[1:]:
            _id = line.split(",")[0]
            job_by_id[_id] = line

    return job_by_id


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

            if ignore_cancelled and p_id in cancelled_packages:
                continue

            if p_id not in package_to_job_ids:
                package_to_job_ids[p_id] = []

            if j_id not in job_to_package_ids:
                job_to_package_ids[j_id] = []

            package_to_job_ids[p_id].append(j_id)
            job_to_package_ids[j_id].append(p_id)

    return [package_to_job_ids, job_to_package_ids]
