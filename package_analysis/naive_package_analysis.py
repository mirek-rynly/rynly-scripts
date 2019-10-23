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
print "Total packages: {}".format(len(package_to_job_ids))
print ""

num_total_nonshipper_jobs = len(nonshipper_job_ids)
num_nonshipper_delivery_jobs = len(nonshipper_delivery_job_ids)
print "Numer of non-shipper jobs: total = {}, pickup = {}, delivery = {}".format(num_total_nonshipper_jobs, num_nonshipper_delivery_jobs, num_total_nonshipper_jobs - num_nonshipper_delivery_jobs)
print "Total shipper jobs: {}".format(len(shipper_job_ids))
print ""

# JOB COST
total_cost_no_shippers = 0
delivery_cost_no_shippers = 0
for _id, job_line in job_by_id.iteritems():

    if _id in shipper_job_ids:
        continue

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
