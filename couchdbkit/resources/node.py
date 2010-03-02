# -*- coding: utf-8 -
#
# This file is part of couchdbkit released under the MIT license. 
# See the NOTICE for more information.

from couchdbkit.resources.base import CouchDbResource
try:
    from simplejson import json
except ImportError:
    import json

    
class Node(CouchDbResource):

    def info(self):
        return self.get()

    def all_dbs(self):
        return self.get('all_dbs')

    def replicate(self, source, target, continuous=False):
        """
        simple handler for replication

        @param source: str, URI or dbname of the source
        @param target: str, URI or dbname of the target
        @param continuous: boolean, default is False, 
        set the type of replication

        More info about replication here :
        http://wiki.apache.org/couchdb/Replication

        """
        return self.post('/_replicate', payload={
        "source": source,
        "target": target,
        "continuous": continuous
        })

    def uuids(self, count=1):
        return self.get('/_uuids', count=count)
        
    
def couchdb_version(server_uri, **client_opts):
    resp = Node(server_uri, **client_opts).info()
    version = json.load(resp.body_file)["version"]
    t = []
    for p in version.split("."):
        try:
            t.append(int(p))
        except ValueError:
            continue
    
    return tuple(t)
    
        