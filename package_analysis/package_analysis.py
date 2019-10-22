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
print "Todal shipper jobs: {}".format(len(shipper_job_ids))

# JOB COST
total_cost_no_shippers = 0
delivery_cost_no_shippers = 0
for _id, job_line in job_by_id.iteritems():

    # _id,JobId,Type,TotalDistance,TrafficTotalTime,TrafficTotalDistance,TotalTime,ActualTotalTime,PayAmount,Shippers,DateCreated,DateCompleted,ContainsExpeditedPackage,
    cost = int(job_line.split(",")[8])
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

for p_id, package_line in package_by_id.iteritems():
    job_id = utils.get_job_id_from_package_line(package_by_id, p_id)
    package_id_to_delivery_job_id[p_id] = job_id


for p_id, j_ids in package_to_job_ids.iteritems():
    if len(set(j_ids)) != len(j_ids):
        raise Exception("Duplicate job ids: {}".format(j_ids))

    for j_id in j_ids:
        j_line = job_by_id[j_id]
        j_num = utils.get_job_number(job_by_id, j_id)

        # best way to determine delivery job is to look at the package line
        # if utils.is_delivery_job(j_line):
        #     # store the most recent delivery job
        #     if p_id not in package_id_to_delivery_job_id:
        #         package_id_to_delivery_job_id[p_id] = j_id
        #     else:
        #         # package was part of a hub-to-hub transfer
        #         last_job_id = package_id_to_delivery_job_id[p_id]
        #         last_job_date = utils.get_job_completed_date(job_by_id, last_job_id)
        #         this_job_date = utils.get_job_completed_date(job_by_id, j_id)
        #         if this_job_date > last_job_date:
        #             # completion data is a good, but not guarenteed, proxy for the "last leg")
        #             package_id_to_delivery_job_id[p_id] = j_id

        if not utils.is_delivery_job(j_line):
            # should be only one pickup job per package
            if p_id in package_id_to_pickup_job_id:
                earlier_job_id = package_id_to_pickup_job_id[p_id]
                raise Exception("Multiple pickup jobs for {}: {} and {}".format(p_id, earlier_job_id, j_id))

            package_id_to_pickup_job_id[p_id] = j_id




fails = 0
for p_id, dj_id in package_id_to_delivery_job_id.iteritems():
    check_dj_id = package_id_to_delivery_job_id_check[p_id]
    if dj_id != check_dj_id:
        print "FAIL for package {} with number {}".format(p_id, utils.get_package_qr_code(package_by_id, p_id))
        old_way_number = utils.get_job_number(job_by_id, dj_id)
        check_way_number = utils.get_job_number(job_by_id, check_dj_id)
        print "Timestamp way job ID: {}, Package db job ID: {}".format(old_way_number, check_way_number)
        fails += 1
        exit(0)

print fails

