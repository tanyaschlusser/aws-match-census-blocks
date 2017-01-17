"""tigerweb_helpers
   ~~~~~~~~~~~~~~~~

    Provide the interface for the census TigerWeb REST server.

    Map REST server documentation:
    http://resources.arcgis.com/en/help/rest/apiref/query.html
"""
import time
import requests

ENDPOINT = 'TIGERweb/tigerWMS_ACS2016/MapServer/'


def get_query(f='json', where='1=1', orderByFields='OBJECTID', **kwargs):
    response = dict(f=f, where=where, orderByFields=orderByFields)
    response.update(kwargs)
    return response


def get_data(endpoint, query={'f': 'pjson'}):
    SERVER = 'https://tigerweb.geo.census.gov/arcgis/rest/services/'
    if 'f' not in query:
        query['f'] = 'pjson'
    response = requests.get(SERVER + endpoint, params=query)
    try:
        data = response.json()
    except ValueError:  # Bad URL; formatted like the server's error messages
        data = {'error': {'message': 'Null response -- total fail'}}
    return data


def iter_features(layer_id, fields='GEOID', step=90000, stop=None):
    """Careful. I think this only works for 'where 1=1' queries...
    ...because it iterates over the OBJECTID, which doesn't necessarily start at zero.
    """
    endpoint = ENDPOINT + '{}/query'.format(layer_id)
    n_obs = get_data(endpoint, query=get_query(where='1=1', returnCountOnly=True))['count']
    # Assume that the observations are numbered from 1 to n_obs
    query = dict(
        f='json',
        where='1=1',  # 'STATE=6 AND CAST(COUNTY AS INTEGER) = 37', -- any SQL query
        outFields=fields,  # '*' -- star to get all the fields
        orderByFields='GEOID',
        returnGeometry=False,
        #outSR='4326',  for latitude and longitude numbers
        #objectIds='242',
        #returnIdsOnly=True,
        #returnCountOnly=True,
    )
    where = '{} <= OBJECTID and OBJECTID < {}'
    if n_obs is not None and n_obs > 0:
        pairs = zip(range(1, n_obs + 1, step), range(step + 1, n_obs + 1 + step, step))
        for pair in pairs:
            print("Getting objects in the range:", pair)
            query['where'] = where.format(*pair)
            result = get_data(endpoint, query=query)
            if 'features' in result and result['features'] is not None:
                for f in result['features']:
                    yield f
            time.sleep(1)
            if stop is not None:
                break
