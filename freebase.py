

#https://www.googleapis.com/freebase/v1/search?query=robot&indent=true&filter=(all%20type:people)
#https://www.googleapis.com/freebase/v1/search?query=tree&indent=true&filter=(all%20type:sports)

import json
import os
import urllib

freebase = urllib.URLopener()
filters = ["people", "location","organization","sports"]
for filter in filters:
    freebaseAPIURL = "https://www.googleapis.com/freebase/v1/search?query="+nerq+"&indent=true&filter=(all%20type:"+filter+")"
    freebase.retrieve(freebaseAPIURL, "search.json")
    json_data=open('search.json')
    data = json.load(json_data)

    json_data.close()
    os.remove('search.json')

