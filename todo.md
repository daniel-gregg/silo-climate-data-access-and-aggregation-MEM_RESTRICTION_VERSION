# To Do list

## update flow
Allow for an alternative flow wherein we assume the rasters can be held on-file.
Loop through each shapefile and calculate target basic (raw) stats
Then loop through again and calculate final statistics for target frequency/stats

This approach allows us to supply a list of shapefiles and to loop through those and so run the program iteratively as new shapefiles come in. The original approach assumes the shapefiles are all fully specified and available and seeks to minimise storage/memory imposts (by removing rasters as relevant calcs are finalised).
