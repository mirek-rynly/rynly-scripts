import os

ANALYSIS_FOLDER = os.path.abspath("/Users/mirek/Desktop/rynly_job_analysis")

package_by_id = {}
#_id,TrackingNumber,DateCreated,AmountPaid,JobId,IsExpedited
with open(os.path.join(ANALYSIS_FOLDER, "prod_packages.csv")) as f_p:
    for line in f_p.read().splitlines()[1:]: # skip header
        _id = line.split(",")[0]
        package_by_id[_id] = line


package_to_job_ids = {}
job_to_package_ids = {}
# job_db_id,JobId,package_db_id
with open(os.path.join(ANALYSIS_FOLDER, "prod_package_to_job_mapping.csv")) as f_ptj:
    for line in f_ptj.read().splitlines()[1:]:
        j_id = line.split(",")[0]
        p_id = line.split(",")[2]

        if p_id not in package_to_job_ids:
            package_to_job_ids[p_id] = []

        if j_id not in job_to_package_ids:
            job_to_package_ids[j_id] = []

        package_to_job_ids[p_id].append(j_id)
        job_to_package_ids[j_id].append(p_id)

job_by_id = {}
shipper_job_ids = set()
delivery_job_ids = set()
# _id,JobId,Type,TotalDistance,TrafficTotalTime,TrafficTotalDistance,TotalTime,ActualTotalTime,PayAmount,Shippers,DateCreated,DateCompleted,ContainsExpeditedPackage,
with open(os.path.join(ANALYSIS_FOLDER, "prod_jobs.csv")) as f_j:
    for line in f_j.read().splitlines()[1:]:
        _id = line.split(",")[0]
        job_by_id[_id] = line

        if line.split(",")[2] == "1": # for Type, 0=pickup, 1=delivery
            delivery_job_ids.add(_id)

        if "ShipperId" in line:
            shipper_job_ids.add(_id)

# SANITY CHECK: looks like two package records don't quite agree
# if len(package_by_id) != len(package_to_job_ids):
#     print "Packages missing in package-to-job mapping:"
#     for p_id in package_by_id:
#         if p_id not in package_to_job_ids:
#             print p_id

#     print "\nPackages missing in packages export:"
#     for p_id in package_to_job_ids:
#         if p_id not in package_by_id:
#             print p_id

num_packages = len(package_to_job_ids)
num_total_jobs = len(job_by_id)
num_delivery_jobs = len(delivery_job_ids)
print "Total packages: {}".format(len(package_to_job_ids))
print "Total jobs: {} ({} delivery)".format(num_total_jobs, num_delivery_jobs)
print "(of the above, {} are shipper jobs)".format(len(shipper_job_ids))

# JOB COST
total_cost_no_shippers = 0
delivery_cost_no_shippers = 0
for _id, job_line in job_by_id.iteritems():
    if _id in shipper_job_ids:
        continue

    # _id,JobId,Type,TotalDistance,TrafficTotalTime,TrafficTotalDistance,TotalTime,ActualTotalTime,PayAmount,Shippers,DateCreated,DateCompleted,ContainsExpeditedPackage,
    cost = int(job_line.split(",")[8])
    total_cost_no_shippers += cost

    if _id in delivery_job_ids:
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
print "Packages per pickup job: {}".format(1.0 * num_packages / (num_total_jobs - num_delivery_jobs))
print "Packages per delivery job: {}".format(1.0 * num_packages / num_delivery_jobs)
