/* Mongo commands to export job / package info for spreadsheet / sql analysis*/
/* global db */

/////////////////////// package_to_job_mapping

// for visualizing
db.Jobs.aggregate([
  {$match: {JobId: 18}},
  {$unwind : "$Packages"},
  {$project: {_id: 0, job_id: "$_id", job_number: "$JobId", package_db_id: "$Packages._id"}},
]).pretty();

// actually create new collection
db.Jobs.aggregate([
  {$unwind : "$Packages"},
  {$project: {_id: 0, job_db_id: "$_id", JobId: 1, package_db_id: "$Packages._id"}},
  {$out: "package_to_job_mapping"}
]);

// exporting to CSV from the command line
// mongoexport --db rynlyproduction --collection package_to_job_mapping --type=csv --fields=job_db_id,JobId,package_db_id > prod_package_to_job_mapping.csv


/////////////////////// packages.csv

// visualizing
db.Packages.find(
  {},
  {From: 0, To: 0, Items: 0, Sender: 0, Recipient: 0, Changes: 0}
);

// export to CSV from command line
// mongoexport --db rynlyproduction --collection Packages --type=csv --fields=_id,TrackingNumber,DateCreated,AmountPaid,JobId,IsExpedited, > prod_packages.csv

// export cancelled packages too (did this later)
// mongoexport --db rynlyproduction --collection Packages --type=csv --fields=_id,TrackingNumber,DateCreated,AmountPaid,JobId,IsExpedited,CancellationNote -q '{"CancellationNote": {"$ne": null}}' > prod_cancelled_packages.csv

/////////////////////// jobs.csv
db.Jobs.find(
  {},
  {Packages: 0, HubLocation: 0, StartLocation: 0}
).pretty();

// export to CSV from command line
// mongoexport --db rynlyproduction --collection Jobs --type=csv --fields=_id,JobId,Type,TotalDistance,TrafficTotalTime,TrafficTotalDistance,TotalTime,ActualTotalTime,PayAmount,Shippers,DateCreated,DateCompleted,ContainsExpeditedPackage, > prod_jobs.csv

// export hub for each job (did this later)
// mongoexport --db rynlyproduction --collection Jobs --type=csv --fields=_id,HubId > prod_hubs_by_job.csv


/////////////////////// misc

// export first two packages changes to determine hub drop-off jobs
// mongoexport --db rynlyproduction --collection Packages --type=csv --fields=_id,Changes.0.Text,Changes.0.AdminChange,Changes.1.Text,Changes.1.AdminChange,Changes.2.Text,Changes.2.AdminChange,Changes.3.Text,Changes.3.AdminChange,Changes.4.Text,Changes.4.AdminChange,Changes.5.Text,Changes.5.AdminChange,Changes.6.Text,Changes.6.AdminChange,Changes.7.Text,Changes.7.AdminChange,Changes.8.Text,Changes.8.AdminChange,Changes.9.Text,Changes.9.AdminChange > package_changes.csv




























