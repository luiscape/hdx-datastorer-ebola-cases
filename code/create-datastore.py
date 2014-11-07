import os
import csv
import json
import scraperwiki
import ckanapi
import urllib
import requests

remote = 'http://data.hdx.rwlabs.org'
APIKey = 'XXXXX'

# ckan will be an instance of ckan api wrapper
ckan = None

def downloadResource(filename):

    # querying
    r = requests.get('https://data.hdx.rwlabs.org/api/action/resource_show?id=f48a3cf9-110e-4892-bedf-d4c1d725a7d1')
    doc = r.json()
    fileUrl = doc["result"]["url"]

    # downloading
    try:
        urllib.urlretrieve(fileUrl, filename)
    except:
        print 'There was an error downlaoding the file.'

def updateDatastore():

    # defining the schema
    resources = [
        {
            'resource_id': 'f48a3cf9-110e-4892-bedf-d4c1d725a7d1',
            'path': 'data/ebola-data-db-format.csv',
            'schema': {
                "fields": [
                  { "id": "Indicator", "type": "text" },
                  { "id": "Country", "type": "text" },
                  { "id": "Date", "type": "timestamp"},
                  { "id": "value", "type": "float" }
                ]
            },
        }
    ]


    def upload_data_to_datastore(ckan_resource_id, resource):
        # let's delete any existing data before we upload again
        try:
            ckan.action.datastore_delete(resource_id=ckan_resource_id, force=True)
        except:
            pass

        ckan.action.datastore_create(
                resource_id=ckan_resource_id,
                force=True,
                fields=resource['schema']['fields'],
                primary_key=resource['schema'].get('primary_key'))

        reader = csv.DictReader(open(resource['path']))
        rows = [ row for row in reader ]
        chunksize = 10000
        offset = 0
        print('Uploading data for file: %s' % resource['path'])
        while offset < len(rows):
            rowset = rows[offset:offset+chunksize]
            ckan.action.datastore_upsert(
                    resource_id=ckan_resource_id,
                    force=True,
                    method='insert',
                    records=rowset)
            offset += chunksize
            print('Done: %s' % offset)


    import sys
    if __name__ == '__main__':
        if len(sys.argv) <= 2:
            usage = '''python scripts/upload.py {ckan-instance} {api-key}

    e.g.

    python scripts/upload.py http://datahub.io/ MY-API-KEY
    '''
            print(usage)
            sys.exit(1)

        remote = sys.argv[1]
        apikey = sys.argv[2]
        ckan = ckanapi.RemoteCKAN(remote, apikey=apikey)

        resource = resources[0]
        upload_data_to_datastore(resource['resource_id'], resource)

def runEverything():
    downloadResource('data/ebola-data-db-format.csv')
    updateDatastore()


# Error handler for running the entire script
try:
    runEverything()
    # if everything ok
    print "Everything seems to be just fine."
    scraperwiki.status('ok')

except Exception as e:
    print e
    scraperwiki.status('error', 'Creating datastore failed')
    os.system("mail -s 'Ebola Case data: creating datastore failed.' luiscape@gmail.com")
