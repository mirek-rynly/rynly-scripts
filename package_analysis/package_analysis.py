import package_utils as utils
import bad_data

def main():
    package_by_id = utils.get_package_by_id_map()
    job_by_id = utils.get_job_by_id_map()
    [package_to_job_ids, _] = utils.get_package_to_jobs_and_job_to_packages()
    [shipper_job_ids, _] = utils.get_shipper_and_nonshipper_job_sets(job_by_id)
    hub_dropoff_packages = bad_data.get_hub_dropoff_packages()
    admin_checked_in_packages = bad_data.get_admin_checked_in_packages()
    admin_delivered_packages = bad_data.get_admin_delivered_packages()

    package_id_to_pickup_job_id = {}
    package_id_to_delivery_job_id = {}

    # 1) USE JOB<->PACKAGE MAPPING FROM THE JOBS COLLECTION
    # This will let us categorize ALL pickup jobs and SOME delivery jobs

    # for these guys we'll use the package line to determine delivery the final job
    multi_job_packages = set()

    packages_without_pickup_job = set()
    for p_id, j_ids in package_to_job_ids.iteritems():
        if len(set(j_ids)) != len(j_ids):
            raise Exception("Duplicate job ids: {}".format(j_ids))

        # why do some packages not have pickup jobs??
        has_pickup = False
        for j_id in j_ids:
            j_line = job_by_id[j_id]
            if not utils.is_delivery_job(j_line):
                has_pickup = True

        # no pickup job if it was a dropoff package or the admin manually "checked it in"
        if not has_pickup and p_id not in hub_dropoff_packages and p_id not in admin_checked_in_packages:
            packages_without_pickup_job.add(p_id)

        for j_id in j_ids:
            j_line = job_by_id[j_id]

            # best way to determine delivery job is to look at the package line
            # here we just sanity check
            if utils.is_delivery_job(j_line):
                if len(j_ids) > 2:
                    multi_job_packages.add(p_id)
                    continue

                if not has_pickup:
                    # missing a pickup job, its not clear which delivery job is the right on
                    # so treat it like any other multi delivery job package
                    multi_job_packages.add(p_id)
                    continue

                package_id_to_delivery_job_id[p_id] = j_id

            else:
                # should be only one pickup job per package
                if p_id in package_id_to_pickup_job_id:
                    earlier_job_id = package_id_to_pickup_job_id[p_id]
                    raise Exception("Multiple pickup jobs for {}: {} and {}".format(p_id, earlier_job_id, j_id))

                package_id_to_pickup_job_id[p_id] = j_id


    # 1) USE JOB DATA STORED IN THE PACKAGE COLLECTION
    # This will let us categorize remaining delivery jobs

    packages_without_job_entries = set()
    undelivered_packages = set() # these guys have a "pickup" job in their job entry
    missing_job_ids = set() # job listed as a package entry but not in jobs export

    for p_id, _ in package_by_id.iteritems():
        job_id_from_package = utils.get_job_id_from_package(package_by_id, p_id)

        # some packages don't have a value in the "job id" field?
        if not job_id_from_package:

            # if an admin manually managed the package it won't have a any job entries
            if p_id in admin_delivered_packages and p_id in admin_checked_in_packages:
                continue

            packages_without_job_entries.add(p_id)
            continue

        # some packages list job ids that don't exist in the jobs collection?
        if job_id_from_package not in job_by_id:
            missing_job_ids.add(job_id_from_package)
            continue

        # check that job is a delivery job (the job entry should be the last job associated
        # with a package, which should always be delivery)
        job_line = job_by_id[job_id_from_package]
        if not utils.is_delivery_job(job_line):

            # if admin manually delivered the package it won't have a delivery job entry
            if p_id in admin_delivered_packages:
                continue

            undelivered_packages.add(p_id)
            continue

        # if we've already categorized this one using job data, it should agree
        if p_id in package_id_to_delivery_job_id:
            prior_delivery_job_match = package_id_to_delivery_job_id[p_id]
            if prior_delivery_job_match != job_id_from_package:
                raise Exception("Current delivery job designation doesn't match existing")

        package_id_to_delivery_job_id[p_id] = job_id_from_package


    # TODO: whats up with all these guys?
    print "Weird stuff:"
    print "Package has no pickup job in Jobs collection: {}".format(len(packages_without_pickup_job))
    print "Package not tagged with any jobs: {}".format(len(packages_without_job_entries))
    print packages_without_job_entries

    # This seem like legit bad data, around 2018 time range?
    print "Package has a pickup job entry in the Packages collection: {}".format(len(undelivered_packages))

    # All but one of the below was completed out of system, corresponding jobs were probably deleted
    print "Job is listed in Package collection but missing in Jobs collection: {}".format(len(missing_job_ids))
    print ""

    packages_missing_pickup_or_delivery = set()
    packages_with_pickup_and_delivery = set()
    uniq_pickup_jobs = set()
    uniq_delivery_jobs = set()

    for p_id in package_by_id:
        if p_id not in package_id_to_pickup_job_id or p_id not in package_id_to_delivery_job_id:
            packages_missing_pickup_or_delivery.add(p_id)
            continue

        pickup_job_id = package_id_to_pickup_job_id[p_id]
        delivery_job_id = package_id_to_delivery_job_id[p_id]

        if pickup_job_id in shipper_job_ids or delivery_job_id in shipper_job_ids:
            raise Exception("Should be no shipper jobs in pickup or final delivery jobs")

        uniq_pickup_jobs.add(pickup_job_id)
        uniq_delivery_jobs.add(delivery_job_id)
        packages_with_pickup_and_delivery.add(p_id)

    if uniq_pickup_jobs.intersection(uniq_delivery_jobs):
        raise Exception("No jobs should be both pickup and delivery")

    ignored_nonshipper_jobs = set()
    for job_id, job_line in job_by_id.iteritems():
        if job_id not in uniq_pickup_jobs and job_id not in uniq_delivery_jobs and job_id not in shipper_job_ids:
            ignored_nonshipper_jobs.add(job_id)

    num_ignored_nonshipper_jobs = len(ignored_nonshipper_jobs)
    print "Num packages missing either pickup or delivery: {}".format(len(packages_missing_pickup_or_delivery))
    print "Num of nonshipper jobs ignored (mostly transfer jobs): {}".format(num_ignored_nonshipper_jobs)
    print ""

    pickup_jobs_cost = get_job_cost(job_by_id, uniq_pickup_jobs)
    delivery_jobs_cost = get_job_cost(job_by_id, uniq_delivery_jobs)
    ignored_nonshipper_jobs_cost = get_job_cost(job_by_id, ignored_nonshipper_jobs) # shipper jobs and transfers
    total_cost = pickup_jobs_cost + delivery_jobs_cost + ignored_nonshipper_jobs_cost

    num_pickup_jobs = len(uniq_pickup_jobs)
    num_delivery_jobs = len(uniq_delivery_jobs)
    total_jobs = num_pickup_jobs + num_delivery_jobs + num_ignored_nonshipper_jobs

    print "Number of nonshipper jobs: total={}, pickup={}, delivery={}, ignored={}".format(total_jobs, num_pickup_jobs, num_delivery_jobs, num_ignored_nonshipper_jobs)
    print "Total cost of nonshipper jobs: total={}, pickup={}, delivery={}, ignored={}".format(total_cost, pickup_jobs_cost, delivery_jobs_cost, ignored_nonshipper_jobs_cost)
    print ""

    print "Cost per nonshipper job: total={}, pickup={}, delivery={}, ignored={}".format(
        1.0 * total_cost / total_jobs, 1.0 * pickup_jobs_cost / num_pickup_jobs,
        1.0 * delivery_jobs_cost / num_delivery_jobs, 1.0 * ignored_nonshipper_jobs_cost / num_ignored_nonshipper_jobs)

    # for packages we have both a pickup and delivery job:
    print "Num packages per job: pickup={}, delivery={}".format(
        1.0 * len(packages_with_pickup_and_delivery) / num_pickup_jobs,
        1.0 * len(packages_with_pickup_and_delivery) / num_delivery_jobs)

def get_job_cost(job_by_id, job_ids):
    total_cost = 0
    for job_id in job_ids:
        job_line = job_by_id[job_id]
        if not job_line:
            raise Exception("Missing job entry")
        total_cost += utils.get_job_cost(job_line)
    return total_cost

if __name__ == "__main__":
    main()
