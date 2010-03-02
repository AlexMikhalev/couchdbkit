# -*- coding: utf-8 -
#
# This file is part of couchdbkit released under the MIT license. 
# See the NOTICE for more information.


from restkit import Resource, HttpConnection, ResourceError
from restkit.util importurl_quote

from couchdbkit.exceptions import ResourceNotFound, ResourceConflict,\
PreconditionFailed, Unauthorized, RequestFailed

try:
    from simplejson import json
except ImportError:
    import json

class CouchDBResponse(HttpResponse):
    
    
    @property
    def json_body(self):
        try:
            return json.load(self.body_file)
        except ValueError:
            return self.body
            

class CouchDBResource(Resource):
    
    def __init__(self, uri, **client_opts):
        Resource.__init__(self, uri=uri, response_class=CouchDBResponse,
                **client_opts)
    
    def request(self, *args, **params):
        headers = params.get('headers') or {}
        headers.setdefault('Accept', 'application/json')
        headers.setdefault('User-Agent', USER_AGENT)
        params['headers'] = headers
        try:
            return Resource.request(self, *args, **params)
        except  ResourceError, e:
            msg = getattr(e, 'msg', '')
            if e.response and msg:
                if e.response.headers.get('content-type') == 'application/json':
                    try:
                        msg = json.loads(msg)
                    except ValueError:
                        pass
                    
            if type(msg) is dict:
                error = msg.get('reason')
            else:
                error = msg
                
            if e.status_int == 404:
                raise ResourceNotFound(error, http_code=404,
                        response=e.response)

            elif e.status_int == 409:
                raise ResourceConflict(error, http_code=409,
                        response=e.response)
            elif e.status_int == 412:
                raise PreconditionFailed(error, http_code=412,
                        response=e.response)
                        
            elif e.status_int in (401, 403):
                raise Unauthorized(str(error))
            else:
                RequestFailed(str(e))
        except Exception, e:
            raise RequestFailed(str(e))
            
def encode_params(params):
    """ encode parameters in json if needed """
    _params = {}
    if params:
        for name, value in params.items():
            if value is None:
                continue
            if name in ('key', 'startkey', 'endkey') \
                    or not isinstance(value, basestring):
                value = json.dumps(value).encode('utf-8')
            _params[name] = value
    return _params    
    
def escape_docid(docid):
    if docid.startswith('/'):
        docid = docid[1:]
    if docid.startswith('_design'):
        docid = '_design/%s' % url_quote(docid[8:], safe='')
    else:
        docid = util.url_quote(docid, safe='')
    return docid
    
def update_doc(res, doc):
    """ quick shortcut to update a doc"""
    if 'id' in res and not '_id' in doc:
        doc['_id'] = res['id']
    if 'rev' in res:
        doc['_rev'] = res['rev']
    return doc
    
def encode_attachments(attachments):
    for k, v in attachments.iteritems():
        if v.get('stub', False):
            continue
        else:
            re_sp = re.compile('\s')
            v['data'] = re_sp.sub('', base64.b64encode(v['data']))
    return attachments