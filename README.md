#  Overview

This repository provides the code necessary to download shapefile data
from the U.S. Census Bureau and map smaller shapes to bigger ones.
The goal is to map all census blocks to larger entities:
counties, congressional districts, state legislative districts,
and school districts, like in the [2010 Census Block Assignment Files][bafs].

Those assignments are just for 2010, and there has since been redistricting.
Plus, the Census updates the data a little every year via the
[American Community Survey][acs] and we want to choose the geography that
matches up to the statistics in those surveys.

So the goal of this work is to:

- Map every Census Block Group to the various desired jurisdictions.
- Use the [Census Geocoder][geocoder] to map every address to a
  Census Block.
- The first 12 digits of Census Block is its Census Block Group
  ([definition of census geoidentifiers][geoid-defs]), so we
  can go from Address → Block → Block Group → any jurisdiction.


### Vocabulary

The geographies change over time. The Census defines a *benchmark* as a
specific survey, like the ACS 2016 survey, and a *vintage* as a data
snapshot for that specific survey (they do two per year I think), so for example
[(from this lookup)][vintages] we see annual vintages, from 2013-2016, for the 2016
ACS survey benchmark...which is I guess the in-progress geographies as they are working
on the 2016 survey.

The specific benchmark and vintage we want depends on the
[Census Gazetteer file][gazetteer] we pick. It says the files match the
ACS survey vintange of their year of publication, so the 2016 Census Gazetteer files
would be tied to the geography in the 2016 vintage of the 2016 ACS survey.
(In other words for the ACS 2016 we want this [map server][acs-rest-geoserver].)


### Logistics

There are [~221k census block groups in the 2010 census][block_tallies],
so if we map 1 per second per legal entity, it would take ~3 days to map
all of them. (And 1 second is kind of wishful). So, this code uses the
AWS EMR service.


<blockquote><h2 style="color:red,background-color:#eee"><em>Warning</em></h2>
<em>Um, since this code use AWS, running it will cost you money.
You should know that though because you'll have had to set up
all of the Amazon parts to get it working. You risk spending tons
of money on stuff left running unless once done,
you confirm that the EMR cluster is terminated
and your S3 buckets removed.<br/><br/>Unless you like giving
your money away, in which case please do send some my way.</em>
</blockquote>



## Usage:

To set up the environment:

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

You also must follow the instructions to [set up Amazon Web Services][aws-setup].
To leave the virtual environment when you're done, type:

```
deactivate
```


### Steps

#### Acquire data

Get every available Census Block Group ID and an interior point inside that Block Group
using the [Census Bureau's tigerWMS_ACS2016 Web server][acs-rest-geoserver].

```
python get_acs2016_block_groups.py
```

Also get all of the shape data; apparently the Census server starts killing the connection
if you pull too much data, so we have to pull it and then send it to S3. Keeping them
as zipfiles will save space, so why not.

```
pass
```

Then copy everything to an AWS S3 bucket

```
aws s3 cp --recursive foo s3://bar  # fix this TANYA
aws s3 cp --recursive foo s3://baz  # fix this TANYA
```

And run the EMR job

```
python run_the_emr_job.py
```


To leave the virtual environment:

```
deactivate
```

Now go check that all of the stuff you don't want running has stopped.
You will of course still be paying for your S3 storage unless you copy
everything down from it and empty and delete the bucket.




## Logistics

The code uses Amazon's Elastic MapReduce service 
to pull the data from the [Census FTP site][census-ftp], extract
the shapefiles, store them on Amazon S3, and then do the matching
of inner shapefile to outer one...



## Census shapefile summary

This section maps the shapefile directory names to their contents.
It was copied (at the last time this README was updated) from a
combination of the [shapefile name definitions][shape-defns]
and the full [2016 shapefile documentation][tiger-doc].

### Legal jurisdictions available from the U.S. Census

- AIANNH
  * American Indian off-reservation trust lands
  * American Indian reservations (both federally and state-recognized)
  * Hawaiian home lands
- ANRC
  * Alaska Native Regional Corporations
- AITSN
  * American Indian tribal subdivisions (within legal American Indian areas)
- CD
  * Congressional districts – 115th Congress
- COUNTY
  * Counties and equivalent entities (except census areas in Alaska)
- STATE
  * States and equivalent entities
- ELSD, SCSD, UNSD
  * School districts (elementary, secondary, and unified)
- SLDU, SLDL
  * State legislative districts (upper and lower chambers)
- SUBMCD
  * Subbarrios (Subminor civil divisions) (Puerto Rico only)
- ESTATE
  * Estates (U.S. Virgin Islands only)
- CONCITY
  * Consolidated cities
- not sure
  * Incorporated places
  * Minor civil divisions (MCDs, such as towns and townships in the Northeast and Midwest)


[acs]: https://www.census.gov/programs-surveys/acs/
[acs-rest-geoserver]: https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2016/MapServer
[aws-setup]: http://docs.aws.amazon.com/cli/latest/userguide/
[bafs]: https://www.census.gov/geo/maps-data/data/baf.html
[block_tallies]: http://www.census.gov/geo/maps-data/data/tallies/all_tallies.html
[census-ftp]: ftp://ftp2.census.gov/geo/tiger/TIGER2016/
[census-hierarchy]: http://www2.census.gov/geo/pdfs/reference/geodiagram.pdf
[gazetteer]: http://www.census.gov/geo/maps-data/data/gazetteer.html
[geocoder]: https://www.census.gov/geo/maps-data/data/geocoder.html
[geoid-defs]: https://www.census.gov/geo/reference/geoidentifiers.html
[shape-defns]: ftp://ftp2.census.gov/geo/tiger/TIGER2016/2016_TL_Shapefiles_File_Name_Definitions.pdf
[tiger-doc]: http://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2016/TGRSHP2016_TechDoc.pdf
[vintages]: https://geocoding.geo.census.gov/geocoder/vintages?benchmark=8
