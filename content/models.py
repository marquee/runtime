import json
from noat       import NOAT
from datetime   import date, datetime

from .fields import *




def _get_field_type_for(name, value):
    """
    Private: return the field for the specified value, either based on the
             type of the value, or based on the suffix of the name. The
             suffixes are a soft convention. Values that do not validate to
             that type are treated like their actual value type. eg fields
             ending in '_date' are checked against the 

    name    - the string name of the field
    value   - the * value of the field

    Returns a subclass of BaseField.
    """

    if name.endswith('_date'):
        try:
            DateTimeField().set(value).validate()
        except ValueError:
            pass
        else:
            return DateTimeField

    if name.endswith('_content'):
        try:
            ContentReferenceField().set(value).validate()
        except ValueError:
            pass
        else:
            return ContentReferenceField

    field_map = (
        (bool       , BooleanField),
        (basestring , StringField),
        (dict       , DictField),
        (int        , IntField),
        (float      , FloatField),
        (list       , ListField),
        (datetime   , DateTimeField),
        (date       , DateTimeField),
    )
    for python_type, field_type in field_map:
        if isinstance(value, python_type):
            return field_type

    # Default to StringField for anything else - in case one of the values is
    # None, for example.
    return StringField 





class _ContentObject(object):

    # The base fields for all content objects (all required), mapped to
    # their corresponding types.
    base_fields = {
            'id'            : (ContentIDField           , dict(none=False)              ),
            'created_date'  : (DateTimeField            , dict(none=False)              ),
            'modified_date' : (DateTimeField            , dict(none=False)              ),
            'owner_id'      : (UserIDField              , dict(none=False)              ),
            'content_md5'   : (MD5Field                 , dict(none=False)              ),
            'annotations'   : (AnnotationListField      , dict(default=[])              ),
            'size'          : (IntField                 , dict(default=0, none=False)   ),
        }

    # Subclasses should define their own fields here. Unfortunately, using
    # dictionaries instead of properties only allows for one level of
    # inheritance, but this method also allows for easy expando behavior.
    # Plus single-level inheritance is probably a good thing in this case.
    fields = {}

    # Ignore these properties when setting them.
    property_blacklist = (
            'type', # set by the class
            'objects',
        )

    immutable_properties = (
            'content_md5',
            'created_date',
            'modified_date',
            'type',
            'size',
            'owner_id',
        )

    def __init__(self, *args, **kwargs):
        # Where the data is actually stored.
        # (Set this way to bypass the __setattr__ below.)
        self.__dict__['_fields'] = {}

        # Set up the base fields as known fields in the model.
        for attr_name, attr_field in self.base_fields.items():
            field_class, field_kwargs = attr_field
            self._fields[attr_name] = field_class(**field_kwargs)
            self._fields[attr_name].name = attr_name

        # Add fields described by the particular model class.
        for attr_name, attr_field in self.fields.items():
            field_class, field_kwargs = attr_field
            self._fields[attr_name] = field_class(**field_kwargs)
            self._fields[attr_name].name = attr_name

        # Initialize from a dictionary passed to the constructor.
        if len(args) > 0:
            if len(args) != 1:
                raise TypeError('ContentObject constructors take at most 1 argument, got %s' % (len(args),))
            
            first_arg = args[0]
            if hasattr(first_arg, 'type'):
                first_arg = first_arg.toDict()
            elif not hasattr(first_arg, 'items'):
                raise ValueError('arguments to ContentObject constructors must be dictionaries')

            for name, value in first_arg.items():
                if name == '_id':
                    name = 'id'
                if not name in self.property_blacklist:
                    setattr(self, name, value)

        # Initialize any data passed through as keyword arguments.
        for name, value in kwargs.items():
            if name == '_id':
                name = 'id'
            if not name in self.property_blacklist:
                setattr(self, name, value)

    def toJSONSafe(self, for_owner=False, **kwargs):
        """
        Public: serialize a JSON-safe representation of the model, for
                consumption through the API.

        Returns a JSON-safe dict.
        """
        data_for_json = {}
        full = kwargs.get('full', False)
        for name, field in self._fields.items():
            # Use the corresponding field to that data item to provide a
            # JSON-safe version of the data.
            if for_owner or not field.owner_only:
                # Nest referenced content objects if full is specified.
                if full and isinstance(field, ContentReferenceField) and name != 'id':
                    data_for_json[name] = field.toJSONSafe(dereference=True)
                else:
                    data_for_json[name] = field.toJSONSafe(**kwargs)
        data_for_json['type'] = self.type
        if not self.id and 'id' in data_for_json:
            data_for_json.pop('id')
        return data_for_json

    def toDict(self, for_owner=False, **kwargs):
        """
        Public: serialize a nearly-JSON-safe representation of the model, for
                consumption through the API. Mostly the same as toJSONSafe,
                but returns DateTimeField values as raw datetimes, instead of
                ISO-formatted strings. (Because dates as strings suck ass when
                doing queries and shit.)

        Returns a nearly-JSON-safe dict.
        """
        data_for_json = {}
        full = kwargs.get('full', False)
        for name, field in self._fields.items():
            if for_owner or not field.owner_only:
                # Nest referenced content objects if full is specified.
                if full and isinstance(field, ContentReferenceField) and name != 'id':
                    data_for_json[name] = field.toJSONSafe(dereference=True)
                elif isinstance(field, DateTimeField):
                    data_for_json[name] = field.get()
                else:
                    data_for_json[name] = field.toJSONSafe(**kwargs)
        data_for_json['type'] = self.type
        if not self.id and 'id' in data_for_json:
            data_for_json.pop('id')
        return data_for_json

    def toJSON(self, **kwargs):
        """
        Public: serialize a JSON representation of the model. Most of the
                time, `toJSONSafe` will be preferred method, to leave
                dumping to a JSON string at the last moment, but `toJSON`
                is for convenience.

        Keyword arguments are passed-through to the `json.dumps` function,
        eg: `modelinstance.toJSON(indent=4)` for pretty printing.

        Returns a string JSON object.
        """
        for_owner = kwargs.pop('for_owner', False)
        return json.dumps(self.toJSONSafe(for_owner=for_owner), **kwargs)

    @property
    def toHTML(self):
        raise NotImplementedError()

    def __getattr__(self, name):
        """
        Public: retrieve the value of the specified attribute.

        Returns the attribute's Python value.
        """
        if name in self._fields:
            return self._fields[name].get()
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        """
        Public: set the specified attribute to the specified value. If the
                attribute has not been set before, it is added to the fields
                of this model instance. The field's type is determined by
                the type of the value, or a particular suffix override if it
                matches.

        Returns nothing.
        """
        field = self._fields.get(name, None)
        if not field:
            field_type = _get_field_type_for(name, value)
            field = field_type()
            field.name = name
            field.is_extra = True
            self._fields[name] = field
        field.set(value)

    def get(self, name, default=None):
        if name in self._fields:
            return self._fields[name].get()
        return default

    def update(self, attrs):
        for k, v in attrs.items():
            setattr(self, k, v)




TEXT_ROLES = [u'paragraph', u'pre', u'quote', u'heading']

class Text(_ContentObject):
    type = 'text'
    fields = {
            'content'   : (StringField, dict(default=u'')         ),
            'role'      : (StringField, dict(default=u'paragraph')),
        }

    def toHTML(self, external_links=False):
        tag_map = {
            'strong'    : 'strong',
            'emphasis'  : 'em',
            'link'      : 'a',
        }
        markup = NOAT(self.content)
        for a in self.annotations:
            if 'url' in a:
                a['href'] = a.pop('url').replace('"','&#34;').replace('\n',' ')
                if len(a['href'].split('://')) > 1 and external_links:
                    a['target'] = '_blank'
            try:
                start = a.pop('start')
                end = a.pop('end')
                a_type = a.pop('type')
            except KeyError:
                pass # Ignore annotations without any of those properties.
            else:
                try:
                    markup.add(tag_map[a_type], start, end, **a)
                except IndexError as e:
                    pass
        return unicode(markup)



class Image(_ContentObject):
    type = 'image'

    fields = {
            'content'   : ( ImageContentField, dict(default={})     ),
            'original'  : ( ImageOriginalField, dict(default={})    ),
        }



class Embed(_ContentObject):
    type = 'embed'

    fields = {
            'content': ( StringField, dict(default=u'') ),
        }



class Container(_ContentObject):
    type = 'container'

    fields = {
            'content': ( ContainerContentField, dict(default=[]) ),
        }



ALL_TYPES = {}
for model_class in (Container, Embed, Image, Text):
    ALL_TYPES[model_class.type] = model_class


def typeClassFromID(object_id):
    obj_type = object_id.split(':')[0]
    return ALL_TYPES[obj_type]

def instanceFromRaw(object_raw):
    if isinstance(object_raw, _ContentObject):
        return object_raw
    type_class = ALL_TYPES[object_raw['type']]
    return type_class(object_raw)
