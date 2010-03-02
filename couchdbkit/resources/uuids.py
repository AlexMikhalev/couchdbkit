# -*- coding: utf-8 -
#
# This file is part of couchdbkit released under the MIT license. 
# See the NOTICE for more information.

from couchdbkit.resources.base import CouchDBResource

class Uuids(CouchDBResource):
    
    def __init__(self, uri, max_uuids=1000, **client_opts):
        super(Uuids, self).__init__(uri, **client_opts)
        
        self._uuids = []
        self.max_uuids = max_uuids
        
    def next(self):
        if not self._uuids:
            self.fetch_uuids()
        self._uuids, res = self._uuids[:-1], self._uuids[-1]
        return res
        
    def __iter__(self):
        return self
        
    def fetch_uuids(self):
        count = self.max_uuids - len(self._uuids)
        resp = self.get('/_uuids', count=count)
        self._uuids += resp.json_body['uuids']