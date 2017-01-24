# noaa.py - example of using api hammer to hammer an api keychain to hammer
# the noaa API

import apihammer,json

conn = apihammer.Connection(service="noaa")
# conn.set_base_url("http://www.ncdc.noaa.gov/cdo-web/api/v2/")
# conn.set_calls_per_second(5)

vk = conn.valid_key()
print "using key", vk

for i in range(0,100 * 1000):
    curr_key = conn.valid_key()
    if curr_key == None:
        print "No keys left!"
        break

    # In a real example, you'd call conn.api_key()
    # every time you need a valid api key.
    # returns None if there are no valid keys
    
    conn.api_key()
    if curr_key["key"] != vk["key"]:
        print "changed to ", curr_key
        vk = curr_key

    


