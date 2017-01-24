# apihammer.py - sometimes you can't be nice
# jake kara
# jake@jakekara.com

import json, datetime, time

def today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

class Keychain:

    def __init__(self,key_file="keys.json",keychain=None):
        self.key_file = key_file
        if (keychain == None):
            self.load()
        else:
            self.keychain = keychain

    def load(self):
        self.keychain = json.loads(open(self.key_file).read())
            
    def keys(self,service=None,key=None):
        if (service == None):
            return self.keychain

        def key_match(obj):
            if (service != None and service.lower() != obj["service"].lower()):
                return False
            if (key != None and key.lower() != obj["key"].lower()):
                return False
            return True

        return filter(lambda x:key_match(x),
                      self.keychain)

    def valid_keys(self,service):
        def is_valid(obj):
            # If there is no calls_per_day, it's not throttled
            if ("calls_per_day" not in obj):
                return True
            # If there are no calls today, it's valid
            if ("last_call" in obj and obj["last_call"] != today()):
                return True
            if ("calls" not in obj):
                return True
            if (obj["calls"] < obj["calls_per_day"]):
                return True

            return False
        return filter(is_valid,self.keys())
        
    def get_last_call(self,service,key):
        obj = self.keys(service=service,key=key)
        if "last_call" not in obj:
            return None
        return obj["last_call"]

    def update_last_call(self,service,key):
        if (self.get_last_call(service,key) == today()):
            return
        obj = self.keys(service=service,key=key)[0]
        obj["last_call"] = today()
        self.write_keychain()

    def calls(self, service, key):
        obj = self.keys(service=service,key=key)[0]
        if "calls" not in obj:
            return None
        return obj["calls"]

    def increment_calls(self, service, key):
        obj = self.keys(service=service,key=key)[0]
        if "calls" not in obj:
            obj["calls"] = 0
        if "last_call" not in obj or obj["last_call"] != today():
            obj["last_call"] = today()
            
        obj["calls"] += 1
        self.write_keychain()
        self.load()
        
    def calls_left(self,service,key):
        obj = self.keys(service=service,key=key)["calls"]

    def write_keychain(self, obj=None,key_file="keys.json"):
        out = open(key_file,"w")
        if (obj==None):
            obj = self.keychain
        
        out.write(json.dumps(obj,indent=2))
        out.close()
    
class Connection:

    def __init__(self, service=None):
        self.cpd = None
        self.cps = None
        self.keychain = Keychain()
        self.service = service
        if (service != None):
            self.keys = self.keychain.keys(service=service)
        self.calls = 0

    def set_base_url(self, burl):
        self.base_url = burl

    def set_calls_per_day(self, cpd):
        self.cpd = cpd

    def set_calls_per_second(self, cps):
        self.cps = cps

    def valid_keys(self):
        return self.keychain.valid_keys(service=self.service)

    def valid_key(self):
        vk = self.valid_keys()
        if len(vk) < 1:
            return None
        return vk[0];
        
    def api_key(self):
        vk = self.valid_key()
        self.keychain.update_last_call(vk["service"],vk["key"])
        self.keychain.increment_calls(vk["service"],vk["key"])
        if (self.cps != None):
            time.sleep( 1 / self.cps)

            return vk["key"]
