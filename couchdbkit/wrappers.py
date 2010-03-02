# -*- coding: utf-8 -
#
# This file is part of couchdbkit released under the MIT license. 
# See the NOTICE for more information.


class ViewResult(object):
    """ View result wrapper::
    
        db = Database("http://someserver/db")
        vres = ViewResul(db.view("ddoc/vname"))
    """
    
    def __init__(self, rst, wrapper=None):
        if hasattr(rst, 'json_body'):
            self.results = rst.json_body
        else:
            self.results = results
        self.wrapper = wrapper

    def __getattr__(self, key):
        try:
            getattr(super(Config, self), key)
        except AttributeError:
            if key in self.results:
                return self.results[key]
            raise
            
    def __getitem__(self):
        try:
            return getattr(self, key)
        except AttributeError:
            pass
        return self.results[key]
        
    def rows(self):
        return list(self)
  
    def next(self):
        for row in self.results['rows']:
            if callable(self.wrapper):
                yield self.wrapper(row)
            else:
                yield row
    
    def __iter__(self):
        return self
        
    def __len__(self):
        return len(self.results['rows'])

    def __nonzero__(self):
        return (len(self) > 0)
        
    
    
            