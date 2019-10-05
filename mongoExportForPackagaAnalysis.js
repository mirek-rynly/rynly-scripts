/* Mongo commands to export job / package info for spreadsheet / sql analysis*/
/* global db */

// for visualizing
db.Jobs.aggregate([
  {$match: {JobId: 18}},
  {$unwind : "$Packages"},
  {$project: {_id: 0, job_id: "$_id", job_number: "$JobId", package_db_id: "$Packages._id"}},
]).pretty();

// actually create new collection
db.Jobs.aggregate([
  {$unwind : "$Packages"},
  {$project: {_id: 0, job_id: "$_id", job_number: "$JobId", package_db_id: "$Packages._id"}},
  {$out: "package_to_job_mapping"}
]).pretty();

// exporting to CSV from the command line
// mongoexport --db rynly --collection package_to_job_mapping --type=csv --fields=job_id,job_number,package_db_id > rynly_job_analysis/package_to_job_mapping.csv
