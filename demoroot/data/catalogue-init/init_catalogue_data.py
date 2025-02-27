import json
import requests
from owslib.ogcapi.records import Records

base_domain = "develop.eoepca.org"
system_catalogue_endpoint = f'https://resource-catalogue.{base_domain}'
collection_id = 'metadata:main'
r = Records(system_catalogue_endpoint)
cat = r.collection(collection_id)

# Create Sentinel 2 L2A collection
record_data = './collections/sentinel-2-l2a.json'
with open(record_data) as fh:
    data = json.load(fh)
collection_identifier = data['id']
r.collection_item_create(collection_id, data)

# Import Sentinel 2 L2A items
stac_items = ["S2A_34SEG_20240721_0_L2A",
              "S2A_34SEH_20240721_0_L2A",
              "S2A_34SFG_20240718_0_L2A",
              "S2A_34SFH_20240721_0_L2A",
              "S2A_34SFH_20240728_0_L2A",
              "S2A_34SFJ_20240721_0_L2A",
              "S2A_34SGH_20240718_0_L2A",
              "S2A_34SGH_20240728_0_L2A",
              "S2A_35SKC_20240718_0_L2A",
              "S2A_35SKC_20240728_0_L2A",
              "S2B_34SGH_20240723_0_L2A",
              "S2B_35SKC_20240723_0_L2A"]

for item in stac_items:
    stac_data = './items/'+item+'.json'
    with open(stac_data) as sf:
        si = json.load(sf)
    identifier = si['id']
    r.collection_item_create(collection_id, si)

# Delete Sentinel 2 L2A items
# for item in stac_items:
#     r.collection_item_delete(collection_id, item)

# Delete Sentinel 2 L2A collectionitems
# r.collection_item_delete(collection_id, collection_identifier)

# Create S2MSI2A collection
record_data = './collections/S2MSI2A.json'
with open(record_data) as fh:
    data = json.load(fh)
collection_identifier = data['id']
r.collection_item_create(collection_id, data)

# Import S2MSI2A items
stac_items = ["S2B_MSIL2A_20190910T095029_N0213_R079_T33TWN_20190910T124513.SAFE",
              "S2B_MSIL2A_20190910T095029_N0213_R079_T33TXN_20190910T124513.SAFE",
              "S2B_MSIL2A_20190910T095029_N0213_R079_T33UWP_20190910T124513.SAFE",
              "S2B_MSIL2A_20190910T095029_N0213_R079_T33UXP_20190910T124513.SAFE",
              "S2B_MSIL2A_20190910T095029_N0213_R079_T33UXQ_20190910T124513.SAFE",
              "S2B_MSIL2A_20190910T095029_N0500_R079_T33TWN_20230430T083712.SAFE",
              "S2B_MSIL2A_20190910T095029_N0500_R079_T33TXN_20230430T083712.SAFE",
              "S2B_MSIL2A_20190910T095029_N0500_R079_T33UWP_20230430T083712.SAFE",
              "S2B_MSIL2A_20190910T095029_N0500_R079_T33UWQ_20230430T083712.SAFE",
              "S2B_MSIL2A_20190910T095029_N0500_R079_T33UXP_20230430T083712.SAFE",
              "S2B_MSIL2A_20190910T095029_N0500_R079_T33UXQ_20230430T083712.SAFE"]

for item in stac_items:
    stac_data = './items/'+item+'.json'
    with open(stac_data) as sf:
        si = json.load(sf)
    identifier = si['id']
    r.collection_item_create(collection_id, si)

# Create S2MSI2C collection
record_data = './collections/S2MSI2C.json'
with open(record_data) as fh:
    data = json.load(fh)
collection_identifier = data['id']
r.collection_item_create(collection_id, data)

# Import S2MSI2A items
stac_items = ["S2B_MSIL1C_20190910T095029_N0208_R079_T33TWN_20190910T120910.SAFE",
              "S2B_MSIL1C_20190910T095029_N0208_R079_T33TXN_20190910T120910.SAFE",
              "S2B_MSIL1C_20190910T095029_N0208_R079_T33UWP_20190910T120910.SAFE",
              "S2B_MSIL1C_20190910T095029_N0208_R079_T33UWQ_20190910T120910.SAFE",
              "S2B_MSIL1C_20190910T095029_N0208_R079_T33UXP_20190910T120910.SAFE",
              "S2B_MSIL1C_20190910T095029_N0208_R079_T33UXQ_20190910T120910.SAFE",
              "S2B_MSIL1C_20190910T095029_N0500_R079_T33TWN_20230429T151337.SAFE",
              "S2B_MSIL1C_20190910T095029_N0500_R079_T33TXN_20230429T151337.SAFE",
              "S2B_MSIL1C_20190910T095029_N0500_R079_T33UWP_20230429T151337.SAFE",
              "S2B_MSIL1C_20190910T095029_N0500_R079_T33UWQ_20230429T151337.SAFE",
              "S2B_MSIL1C_20190910T095029_N0500_R079_T33UXP_20230429T151337.SAFE",
              "S2B_MSIL1C_20190910T095029_N0500_R079_T33UXQ_20230429T151337.SAFE"]

for item in stac_items:
    stac_data = './items/'+item+'.json'
    with open(stac_data) as sf:
        si = json.load(sf)
    identifier = si['id']
    r.collection_item_create(collection_id, si)