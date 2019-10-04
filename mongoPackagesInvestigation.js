/*
Mongo REPL queries to get a sense for why the DeliveryLocation
attribute in the Packages collection means.

Conclusion: it's probably a legacy thing that's no longer used.
*/

/* global db, print */
"use strict"; // jshint -W097

// number of entries (485)
db.Packages.count();

// number of entries with delivery attribute (485)
db.Packages.count({DeliveryLocation: {$exists: true}});

// number of entries with a non-null value for said attribute (38)
db.Packages.count({DeliveryLocation: {$exists: true, $ne: null}});

// print 'location' coordinate vs 'from' and 'to' coordinates
var uniq = {};
db.Packages.find({DeliveryLocation: {$exists: true, $ne: null}}).forEach((x) => {
  var deliveryStr = `${x.DeliveryLocation.Longitude},${x.DeliveryLocation.Latitude}`; // why do we do this backwards?
  print(`D Location: ${deliveryStr}`);
  print(`F Location: ${x.From.Location.coordinates}`);
  print(`T Location: ${x.To.Location.coordinates}\n`);

  if (!uniq[deliveryStr]) {
    uniq[deliveryStr] = 0;
  }
  uniq[deliveryStr] += 1;
});

// print histogram of unique work coordinates
for (var key in uniq) {
  print(`${key}: ${uniq[key]}`);
}


