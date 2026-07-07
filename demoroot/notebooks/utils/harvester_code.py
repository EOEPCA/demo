import requests



def odata_query(api_url, query_filter):
    """
    Searches for data in ESA Copernicus Data Space Ecosystem based on a given query filter

    Arguments:
        api_url: API URL
        query_filter: Query string to be passed to the API URL

    Returns:
        (Array): List of scenes
    """

    query_url = api_url + query_filter

    scenes = []
    while query_url is not None:
        print(f"Executing OData query: {query_url}")
        res = requests.get(query_url)
        if res.status_code == 200:
            data = res.json()
            print("Found %s scenes" % len(data["value"]))
            for feature in data["value"]:
                scene = dict(
                    uid=feature["Id"],
                    scene_id=feature["Name"],
                    S3Path=feature["S3Path"],
                    GeoFootprint=feature["GeoFootprint"],
                    ContentLength=feature["ContentLength"],
                    PublicationDate=feature["PublicationDate"],
                    ModificationDate=feature["ModificationDate"],
                )
                if "Attributes" in feature:
                    for attr in feature["Attributes"]:
                        scene[attr["Name"]] = attr["Value"]
                scenes.append(scene)
        else:
            query_url = None
            raise ValueError(f"Error executing OData query: {res.status_code} {res.content}")

        if "@odata.nextLink" in data:
            print("More results availble. Retrieving next page of result set ...")
            query_url = data["@odata.nextLink"]
        else:
            print("Result set complete")
            query_url = None
        breakpoint()
    return scenes


def search(api_url, max_items, filters):
    """
    Description...

    Parameters:
        api_url
        max_items
        filters

    Returns:
        list of scenes found
    """
    # query_template = "/Products?$filter=%filter&$top=" + str(max_items)
    # if filters is None:
    #    filters = [
    #        (
    #            "(startswith(Name,'S1') and (contains(Name,'SLC') or contains(Name,'GRD')) "
    #            "and not contains(Name,'_COG') and not contains(Name, 'CARD_BS'))&$expand=Attributes"
    #        ),
    #        "(startswith(Name,'S2') and (contains(Name,'L2A')) and not contains(Name,'_N9999'))",
    #        # ("(startswith(Name,'S2') and (contains(Name,'L1C') or
    #        # contains(Name,'L2A')) and not contains(Name,'_N9999'))"),
    #        # "(startswith(Name,'S3A') or startswith(Name,'S3B'))",
    #        # "(startswith(Name,'S5P') and not contains(Name,'NRTI_'))"
    #    ]

    scenes = []
    if len(filters) == 0:
        query_url = f"/Products?$top={max_items}"
        scenes_found = odata_query(api_url=api_url, query_filter=query_url)
        print("%s scenes found" % len(scenes_found))
        scenes.extend(scenes_found)
    else:
        for filter in filters:
            # filter_all = filter_base + " and " + filter
            query_url = f"/Products?$filter={filter}&$top={max_items}"
            # query_url = query_template.replace("%filter", filter_all)
            scenes_found = odata_query(api_url=api_url, query_filter=query_url)
            scenes.extend(scenes_found)

    return scenes