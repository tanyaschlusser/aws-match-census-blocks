"""get_acs2016_block_groups
   ~~~~~~~~~~~~~~~~~~~~~~~~

    Create a directory 'blockgroups2016' and fills it with files
    blockgroups2016/<STATE-FIPS>.txt that contain JSONs with the
    census block groups and interior points for that state.
"""
import json
import os
import tigerweb_helpers as tiger

BLOCKGROUPS = 'Census Block Groups'
DESTINATION_DIR = 'blockgroups2016'


# ---------------------------------------------------------------- Main
if not os.path.exists(DESTINATION_DIR):
    os.makedirs(DESTINATION_DIR)

response = tiger.get_data(tiger.ENDPOINT)
block_group_layer = next(
    entry for entry in response['layers']
    if entry['name'] == BLOCKGROUPS
)

file_handles = {}
fields = ('BLKGRP', 'STATE', 'COUNTY', 'NAME', 'GEOID', 'OBJECTID', 'INTPTLAT', 'INTPTLON')
for f in tiger.iter_features(block_group_layer['id'], fields=','.join(fields)):
    attrib = f['attributes']
    state = attrib['STATE']
    if state not in file_handles:
        destination = os.path.join(DESTINATION_DIR, state + '.txt')
        file_handles[state] = open(destination, 'w')
    # The file is not itself a JSON object, but rows of individual dictionaries.
    file_handles[state].write(json.dumps(attrib))
    file_handles[state].write('\n')

for fh in file_handles.values():
    fh.close()
