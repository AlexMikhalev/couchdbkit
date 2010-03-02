# -*- coding: utf-8 -
#
# This file is part of couchdbkit released under the MIT license. 
# See the NOTICE for more information.

import itertools
import mimetypes
import tempfile

from couchdbkit.resources.base import CouchDBResource, encode_attachments,\
escape_docid, url_quote
from couchdbkit.resources.uuids import Uuids

try:
    from simplejson import json
except ImportError:
    import json

class Database(CouchDBResource):
    
    def __init__(self, uri, create=True, **client_opts):
        super(Database, self).__init__(uri, **client_opts)

        self.ui = ui
        self.server_uri = uri.rsplit('/', 1)[0]
        self.uuids = Uuids(self.server_uri)
        self.version = couchdb_version(self.server_uri, **client_opts)
        
        # create the db
        if create:
            try:
                self.head()
            except ResourceNotFound:
                self.put()
                
    def create(self):
        """ create the database """
        return self.put()
        
    def delete(self):
        """ delete itself """
        return self.delete()
        
    def info(self):
        return self.get()
            
    def __call__(self, path):
        new_uri = self._make_uri(self.uri, path)
        return type(self)(self.ui, new_uri)
            
    def open_doc(self, docid=None, wrapper=None, *params):
        docid = docid or self.uuids.next()
        resp = self.get(escape_docid(docid), *params)
        
        if wrapper is not None:
            if not callable(wrapper):
                raise TypeError("wrapper isn't a callable")
            return wrapper(resp)
        return resp
        
    def save_doc(self, doc=None, encode=False, **params):
        doc = doc or {}
        if '_attachments' in doc and (encode and self.version < (0, 11)):
            doc['_attachments'] = encode_attachments(doc['_attachments'])
         
        with tempfile.TemporaryFile() as json_stream:
            # we use a temporary file to send docs to reduce 
            # memory usage
            json.dump(doc, json_stream)
            
            res = None
            if '_id' in doc:
                docid = escape_docid(doc['_id'])
                res = self.put(docid, payload=json_stream, **params)
            else:
                try:
                    doc['_id'] = self.uuids.next()
                    res = self.put(doc['_id'], payload=json_stream, **params)
                except ResourceConflict:
                    res = self.post(payload=json_stream, **params)
                
            return res
            
    def delete_doc(self, id_or_doc, rev=None, **params):
        if isinstance(id_or_doc, basestring):
            docid = id_or_doc
        else:
            docid = id_or_doc['_id']
            if '_rev' in doc and not rev:
                rev = doc['_rev']
        if not rev:
            resp = self.head(escape_docid(doc['_id']))
            rev = resp.headers['etag'].strip('""')
        
        return self.delete(docid, rev=rev,**params)
        
    def save_docs(sef, docs, all_or_nothing=False, use_uuids=True):       
        def is_id(doc):
            return '_id' in doc
            
        if use_uuids:
            ids = []
            noids = []
            for k, g in itertools.groupby(docs, is_id):
                if not k:
                    noids = list(g)
                else:
                    ids = list(g)
                    
            for doc in noids:
                nextid = self.uuids.next()
                if nextid:
                    doc['_id'] = nextid
                    
        payload = { "docs": docs }
        if all_or_nothing:
            payload["all-or-nothing"] = True
            
        # update docs
        with tempfile.TemporaryFile() as json_stream:
            json.dump(payload, json_stream)
            return self.post('/_bulk_docs', payload=json_stream)
            
    def delete_docs(self, docs, all_or_nothing=False):
        for doc in docs:
            doc['_deleted'] = True
        return self.save_docs(docs, all_or_nothing=all_or_nothing)

    def fetch_attachment(self, id_or_doc, name):
        if isinstance(id_or_doc, basestring):
            docid = id_or_doc
        else:
            docid = id_or_doc['_id']
      
        return self.get("%s/%s" % (escape_docid(docid), name))
        
    def put_attachment(self, doc, content=None, name=None, content_type=None, 
            content_length=None):
            
        headers = {}
        
        if not content:
            content = ""
            content_length = 0
            
        if name is None:
            if hasattr(content, "name"):
                name = content.name
            else:
                raise InvalidAttachment(
                            'You should provid a valid attachment name')
        name = url_quote(name, safe="")
        
        if content_type is None:
            content_type = ';'.join(filter(None, mimetypes.guess_type(name)))

        if content_type:
            headers['Content-Type'] = content_type
            
        # add appropriate headers    
        if content_length and content_length is not None:
            headers['Content-Length'] = content_length

        return self.put("%s/%s" % (escape_docid(doc['_id']), name), 
                    payload=content, headers=headers, rev=doc['_rev'])
                    
    def delete_attachment(self, doc, name):
         name = resource.url_quote(name, safe="")
         return self.delete("%s/%s" % (escape_docid(doc['_id']), name), 
                        rev=doc['_rev'])
                        
    def all_docs(self, **params):
        if 'keys' in params:
            payload = json.dump({keys: params.pop('keys')})
            return self.post(view_path, payload=payload, **params)
        
        return self.get('_all_docs', **params)
         
    def view(self, view_name, **params):
        if isinstance(view_name, tuple):
            (dname, vname) = view_name
        else:        
            view_name = view_name.split('/')
            dname = view_name.pop(0)
            vname = '/'.join(view_name)
            
        view_path = '_design/%s/_view/%s' % (dname, vname)
        if 'keys' in params:
            payload = json.dump({keys: params.pop('keys')})
            return self.post(view_path, payload=payload, **params)
        return self.get(view_path, **params)
        


