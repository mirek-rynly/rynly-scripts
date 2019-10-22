import package_utils as utils

package_by_id = utils.get_package_by_id_map()
job_by_id = utils.get_job_by_id_map()
[package_to_job_ids, job_to_package_ids] = utils.get_package_to_jobs_and_job_to_packages()
[shipper_job_ids, nonshipper_job_ids] = utils.get_shipper_and_nonshipper_job_sets(job_by_id)
[_, nonshipper_delivery_job_ids] = utils.get_shipper_and_nonshipper_job_sets(job_by_id, True)

# SANITY CHECK: looks like two package records don't quite agree
# if len(package_by_id) != len(package_to_job_ids):
#     print "Packages missing in package-to-job mapping ({} != {}):".format(len(package_by_id), len(package_to_job_ids))
#     for p_id in package_by_id:
#         if p_id not in package_to_job_ids:
#             print p_id

#     print "\nPackages missing in packages export:"
#     for p_id in package_to_job_ids:
#         if p_id not in package_by_id:
#             print p_id


num_packages = len(package_to_job_ids)
num_total_nonshipper_jobs = len(nonshipper_job_ids)
num_nonshipper_delivery_jobs = len(nonshipper_delivery_job_ids)
print "Total packages: {}".format(len(package_to_job_ids))
print "Total non-shipper jobs: {} ({} delivery)".format(num_total_nonshipper_jobs, num_nonshipper_delivery_jobs)
print "Total shipper jobs: {}".format(len(shipper_job_ids))

# JOB COST
total_cost_no_shippers = 0
delivery_cost_no_shippers = 0
for _id, job_line in job_by_id.iteritems():

    # _id,JobId,Type,TotalDistance,TrafficTotalTime,TrafficTotalDistance,TotalTime,ActualTotalTime,PayAmount,Shippers,DateCreated,DateCompleted,ContainsExpeditedPackage,
    cost = utils.get_job_cost(job_line)
    total_cost_no_shippers += cost

    if _id in nonshipper_delivery_job_ids:
        delivery_cost_no_shippers += cost

print "Cost of all (non-shipper) jobs: total = {}, cost per package = {}".format(total_cost_no_shippers, 1.0 * total_cost_no_shippers / num_packages)
print "Cost of (non-shipper) delivery jobs: total = {}, average = {}".format(delivery_cost_no_shippers, 1.0 * delivery_cost_no_shippers / num_packages)
print ""

total_cost_of_shippers = len(shipper_job_ids) * 200.0
total_cost_with_shippers = total_cost_no_shippers + total_cost_of_shippers
print "Cost of shipper jobs (assuming $200 / job): {}".format(total_cost_of_shippers)
print "Cost of all jobs (including shippers): total = {}, cost per package = {}".format(total_cost_with_shippers, total_cost_with_shippers / num_packages)
print ""

# ROUGH PACKAGES PER JOB
print "Packages per pickup job: {}".format(1.0 * num_packages / (num_total_nonshipper_jobs - num_nonshipper_delivery_jobs))
print "Packages per delivery job: {}".format(1.0 * num_packages / num_nonshipper_delivery_jobs)
print ""

# EXACT PACKAGES PER JOB
package_id_to_pickup_job_id = {}
package_id_to_delivery_job_id = {}

# 1) USE JOB -> PACKAGE MAPPING FROM THE JOBS COLLECTION
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

    if not has_pickup:
        packages_without_pickup_job.add(p_id)

    for j_id in j_ids:
        j_line = job_by_id[j_id]
        j_num = utils.get_job_number(job_by_id, j_id)

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

for p_id, package_line in package_by_id.iteritems():
    job_id_from_package = utils.get_job_id_from_package(package_by_id, p_id)

    # some packages don't have job id entries?
    if not job_id_from_package:
        packages_without_job_entries.add(p_id)
        continue

    # some packages list job ids that don't exist in the packages collection?
    if job_id_from_package not in job_by_id:
        missing_job_ids.add(job_id_from_package)
        continue

    # check that job is a delivery job
    job_line = job_by_id[job_id_from_package]
    if not utils.is_delivery_job(job_line):
        undelivered_packages.add(p_id)
        continue

    # if we've already categorized this one using job data, it should agree
    if p_id in package_id_to_delivery_job_id:
        prior_delivery_job_match = package_id_to_delivery_job_id[p_id]
        if prior_delivery_job_match != job_id_from_package:
            raise Exception("Current delivery job designation doesn't match existing")

    package_id_to_delivery_job_id[p_id] = job_id_from_package


# TODO: whats up with all these guys?
print "Weird stuff"
print "no pickup job: {}".format(len(packages_without_pickup_job))
print "job entryless: {}".format(len(packages_without_job_entries))
print "undelivered: {}".format(len(undelivered_packages))
print "missing job ids: {}".format(len(missing_job_ids))
print ""

missing_pickup_or_delivery = set()

uniq_pickup_jobs = set()
uniq_delivery_jobs = set()
pickup_jobs_cost = 0
delivery_jobs_cost = 0

for p_id in package_by_id:
    if p_id not in package_id_to_pickup_job_id or p_id not in package_id_to_delivery_job_id:
        missing_pickup_or_delivery.add(p_id)
        continue

    pickup_job_id = package_id_to_pickup_job_id[p_id]
    delivery_job_id = package_id_to_delivery_job_id[p_id]

    pickup_job_line = job_by_id[pickup_job_id]
    delivery_job_line = job_by_id[delivery_job_id]
    if not pickup_job_line or not delivery_job_line:
        raise Exception("No job entry corresponding to mapped job")

    uniq_pickup_jobs.add(pickup_job_id)
    uniq_delivery_jobs.add(delivery_job_id)

    pickup_jobs_cost += utils.get_job_cost(pickup_job_line)
    delivery_jobs_cost += utils.get_job_cost(delivery_job_line)

print "Ignored b/c either pickup or delivery was missing: {}".format(len(missing_pickup_or_delivery))
print ""

num_pickup_jobs = len(uniq_pickup_jobs)
num_delivery_jobs = len(uniq_delivery_jobs)
print "Number of jobs: total={}, pickup={}, delivery={}".format(num_pickup_jobs + num_delivery_jobs, num_pickup_jobs, num_delivery_jobs)
print "Total cost of jobs: total={}, pickup={}, delivery={}".format(pickup_jobs_cost + delivery_jobs_cost, pickup_jobs_cost, delivery_jobs_cost)
