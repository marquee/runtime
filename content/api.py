
DEFAULT_API_ROOT = 'marquee.by/content/'

import requests, json

class ContentAPIWrapper(object):
    def __init__(self, api_token, api_root):
        self._token     = api_token
        self._api_root  = api_root


    def _prepareHeaders(self, headers={}):
        headers.update({
                'Authorization'         : 'Token {0}'.format(self._token),
                'Content-Type'          : 'application/json',
                'X-Include-Published'   : True,
            })
        return headers


    def baseURL(self):
        return 'http://{0}'.format(self._api_root)

    def instanceURL(self, object_id):
        return 'http://{0}{1}/'.format(self._api_root, object_id)


    def readInstance(self, instance):
        r = requests.get(
                self.instanceURL(instance.id),
                headers = self._prepareHeaders(),
            )
        if r.status_code != 200:
            raise Exception(r.content)
        instance.update(json.loads(r.content))
        return instance

    def createInstance(self, instance):
        r = requests.post(
                self.baseURL(),
                headers = self._prepareHeaders(),
                data    = instance.toJSON(),
            )
        if r.status_code != 201:
            raise Exception(r.content)
        instance.update(json.loads(r.content))
        return instance

    def updateInstance(self, instance):
        r = requests.put(
                self.instanceURL(instance.id),
                headers = self._prepareHeaders(),
                data    = instance.toJSON(),
            )
        if r.status_code != 200 or r.status_code != 204:
            raise Exception(r.content)
        instance.update(json.loads(r.content))
        return instance

    def deleteInstance(self, instance):
        r = requests.delete(
                self.instanceURL(instance.id),
                headers = self._prepareHeaders(),
            )
        return None

    def readList(self, query, constraints={}):
        # send query as JSON? - takes care of boolean/None values
        constraints = self._constraintsToHeaders(constraints)
        r = requests.get(
                self.baseURL(),
                headers = self._prepareHeaders(constraints),
                params = query,
            )
        if r.status_code != 200:
            raise Exception(r.content)
        return json.loads(r.content)

    def _constraintsToHeaders(self, constraints):
        headers = {}
        for k, v in constraints.items():
            key = "X-Content-Query-{0}".format(k.capitalize())
            headers[key] = v
        print headers
        return headers

from .models import ALL_TYPES, typeClassFromID, instanceFromRaw



class APIQueryException(Exception): pass



# Constructs a query by adding these constraints to headers
class APIQuery(object):

    def __init__(self, api, params):
        self._api           = api
        self._params        = params
        self._constraints   = {}
        self._result        = None
        self._output_map    = lambda x: x

    def _hasExecuted(self):
        return (not self._result is None)

    def limit(self, n):
        if self._hasExecuted():
            raise APIQueryException('Query has been executed. Cannot apply limit.')
        self._constraints['limit'] = n
        return self

    def sort(self, sort):
        if self._hasExecuted():
            raise APIQueryException('Query has been executed. Cannot apply sort.')
        self._constraints['sort'] = sort
        return self

    def offset(self, n):
        if self._hasExecuted():
            raise APIQueryException('Query has been executed. Cannot apply offset.')
        self._constraints['offset'] = n
        return self

    def execute(self):
        if self._result is None: 
            print self._params
            print self._constraints
            result = self._api.readList(self._params, constraints=self._constraints)
            self._result = map(lambda x: self._output_map(instanceFromRaw(x)), result)
        return self._result

    def __len__(self):
        return len(self.execute())

    def __iter__(self):
        return iter(self.execute())

    # TODO: support slicing, lazy offsets (needs to copy queryset)
    def __getitem__(self, index):
        return self.execute()[index]

    def undo(self):
        self._result = None
        return self

    def map(self, fn):
        return map(fn, self.execute())

    def mapOnExecute(self, fn):
        self._output_map = fn
        return self

class ContentObjects(object):

    def __init__(self, api_token, api_root=DEFAULT_API_ROOT):
        self._api           = ContentAPIWrapper(api_token, api_root)
        self.TOKEN          = api_token
        self.ROOT           = api_root

    def fetch(self, object_id):
        obj = typeClassFromID(object_id)(id=object_id)
        return self._api.readInstance(obj)

    def create(self, type_class, attrs):
        # If `type_class` is a string, convert it to a type class.
        if not hasattr(type_class, 'type'):
            type_class = ALL_TYPES[type_class]
        obj = type_class(**attrs)
        self._api.createInstance(obj)
        return obj

    def filter(self, *args, **kwargs):
        
        # Allow for calling with `type=Text`.
        if 'type' in kwargs and hasattr(kwargs['type'], 'type'):
            kwargs['type'] = kwargs['type'].type

        query = APIQuery(self._api, kwargs)
        return query
        
    def all(self):
        return self.filter()

    # Instead of on the instance, because trying to pass the api object around is a fucking mess
    def save(self, *args):
        for arg in args:
            def _saveItem(item):
                if self.id:
                    self._api.updateInstance(self)
                else:
                    self._api.createInstance(self)
            if hasattr(arg, 'id'):
                _saveItem(arg)
            else:
                for a in arg:
                    _saveItem(a)
        return



