# coding: utf-8

from dateutil   import parser
from datetime   import datetime
from uuid       import uuid4, UUID
from urllib     import quote

import pytz, hashlib, copy



class BaseField(object):

    def __init__(self, default=None, none=True, choices=None, owner_only=False,):
        """
        Public: construct an instance of BaseField.

        default     - (optional:None) the default value of the field.
        none        - (optional:True) Boolean flag if None is an acceptible value
        choices     - (optional:None) a list/tuple of the possible values the field can take.
                      If none=True, None will be an acceptible value *in addition to* the
                      choices specified.
        owner_only  - (optional:False) Boolean flag whether or not the field is intended
                      only for representations for the owner of the object. (The model will
                      exclude owner_only=True fields from JSON dumps for non-owners.)
        """
        self._value             = copy.deepcopy(default)
        self._possible_values   = choices
        self.owner_only         = owner_only
        self._allows_none       = none
        self.name               = ''            # Set by the model. Not really
                                                # necessary, but provides
                                                # better error feedback.

        # Make sure None is acceptible if choices are specified and `none=True`.
        if self._allows_none and self._possible_values and not None in self._possible_values:
            self._possible_values.append(None)

    def set(self, value):
        """
        Public: set the value of the field. Runs the value through the field's
                defined `parse` function, but does not validate. However, the
                `parse` function MAY raise a `ValueError` if it is unable to
                parse the value.

        Returns self for chaining.
        """
        self._value = self.parse(value)
        return self

    def get(self):
        """
        Public: get the value of the field.

        Returns a Python type.
        """
        return self._value

    def validate(self):
        """
        Public: validate the field's data. This performs general validation
                common to all fields (checking for `None`, verifying choices).
                Type-specific validation should be defined in a
                `_type_validate` method on the inheriting class.

        Returns a Boolean True if the field is valid, raises an exception if
        not valid.
        """

        if not self._allows_none and self._value == None:
            raise ValueError("%s does not allow None" % (self.name,))
        if self._possible_values and not self._value in self._possible_values:
            raise ValueError("%s (%s) must be one of %s" % (self.name, self._value, self._possible_values))

        self._type_validate()

        return True


    # These methods should be overridden by the extending field class if needed:

    def toJSONSafe(self, **kwargs):
        """
        Public: provide a JSON-safe representation of the field's value. This
                MUST be JSON-serializable by the `json.dumps` function.

        Returns an int, float, str, None, Boolean, list, or dict.
        (Dictionaries and lists MUST be empty or contain only these types.)
        """
        return copy.deepcopy(self._value)

    def _type_validate(self):
        """
        Private: perform validations specific to the type, if necessary. MUST
                 raise an exception if `self._value` is not valid. MUST allow
                 for None to be valid (validated by `validate` instead).

        Returns Boolean True.
        """
        return True

    @staticmethod
    def parse(value):
        """
        Public: parse the incoming data to be set on the field. Fields SHOULD
                 be fairly liberal in what they accept, except in cases where
                 information could be lost, eg the DateTimeField accepts
                 various date/time representations, while the IntField does
                 not accept floats. The field's overridden version MUST be a
                 `@staticmethod`.

        value - incoming data of potentially any type.

        Returns the value to store.
        """
        return value



class DateTimeField(BaseField):
    """
    Public: a field that stores and handles `datetime` values. The value is
            stored in Mongo as a BSON Date, but serialized to JSON as an
            ISO-format string.

    The field is fairly liberal in what it can be set to. Anything that
    resembles a date will be converted to a `datetime`. This includes various
    string formats, and POSIX timestamps. The datetime is always stored in UTC.
    Formats that specify a timezone will be converted accordingly. Formats
    without a timezone will be assumed UTC.

    Acceptible formats include:

        "2013-03-05T23:09:13.12345Z"
        "2013-03-05T23:09:13-05:00"
        "2013-03-05 23:09:13-05:00"
        "2013-03-05 23:09:13"
        "3/5/2013 23:09:13"
        "2013-03-05"
        1363122028
        1363122028.1234

    For more valid formats, see: http://labix.org/python-dateutil#head-a23e8ae0a661d77b89dfb3476f85b26f0b30349c
    """

    @staticmethod
    def parse(value):
        """
        Private: parse the incoming value into a `datetime`.

        Returns a datetime or None.
        """
        if not value:
            return None

        if not hasattr(value, 'strftime'):
            try:
                value = float(value)
            except ValueError:
                value = parser.parse(value) # Raises an error if unable to parse
            else:
                value = datetime.fromtimestamp(value)

        # Ensure the date is being stored in UTC format
        if not value.tzinfo:
            value = value.replace(tzinfo=pytz.utc)
        else:
            value = value.astimezone(pytz.utc)
    
        return value

    def toJSONSafe(self, **kwargs):
        """
        Public: provide a JSON-safe version of this field's value.

        Returns an ISO-format
        """
        if hasattr(self._value, 'strftime'):
            return self._value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            return None



class IntField(BaseField):
    """
    Public: a field that stores an int.

    The value MUST be an int or None. The field will NOT coerce.
    """

    def _type_validate(self):
        if self._value != None and (not isinstance(self._value, int) or isinstance(self._value, bool)):
            raise ValueError('%s must be of type int, got %s' % (
                        self.name,
                        type(self._value),
                    )
                )



class FloatField(BaseField):
    """
    Public: a field that stores a float.

    The value MUST be a float, an int, or None. (If int, will cast to float.)
    """

    @staticmethod
    def parse(value):
        if value != None:
            if not isinstance(value, bool) and isinstance(value, int):
                value = float(value)
        return value

    def _type_validate(self):
        if self._value != None and not isinstance(self._value, float):
            raise ValueError('%s must be of type float, got %s' % (
                        self.name,
                        type(self._value),
                    )
                )



class DictField(BaseField):
    """
    Public: a field that stores a dict.

    """
    def _type_validate(self):
        if self._value != None and not isinstance(self._value, dict):
            raise ValueError('%s must be of type dict, got %s' % (
                        self.name,
                        type(self._value),
                    )
                )

    def toJSONSafe(self, **kwargs):
        """
        Public: provide a JSON-safe version of this field's value.

        Returns a dictionary that can be serialized by the `json.dumps` function.
        """
        if not self._value:
            return self._value

        # TODO: Make this fully inspect the object, not just the first level.
        output = {}
        for k, v in self._value.items():
            if hasattr(v, 'strftime'):
                output[k] = v.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                output[k] = v
        return output



class ListField(BaseField):
    """
    Public: a field that stores a list.

    The value MUST be None, a list, a set, or a tuple. (sets or tuples will be cast to a list.)
    """
    @staticmethod
    def parse(value):
        if value != None:
            if isinstance(value, set) or isinstance(value, tuple):
                value = list(value)
        return value

    def _type_validate(self):
        if self._value != None and not isinstance(self._value, list):
            raise ValueError('%s must be of type list, got %s' % (
                        self.name,
                        type(self._value),
                    )
                )



class StringField(BaseField):
    """
    Public: a field that stores a `unicode`.

    The value MUST be an instance of basestring, and will be cast to unicode,
    or None.
    """

    @staticmethod
    def parse(value):
        if value != None:
            if isinstance(value, basestring):
                value = unicode(value)
        return value

    def _type_validate(self):
        if self._value != None and not isinstance(self._value, unicode):
            raise ValueError('%s must be a unicode or None. Got %s (%s)' % (self.name, self._value, type(self._value)))
        return True


class BooleanField(BaseField):
    """
    Public: a field that stores a Boolean (or None).

    'false' and 'true' will be converted to False and True, respectively.
    """

    @staticmethod
    def parse(value):
        if value == 'false':
            return False
        if value == 'true':
            return True
        return value

    def _type_validate(self):
        if self._value != None and not isinstance(self._value, bool):
            raise ValueError('%s must be of type bool, got %s' % (
                        self.name,
                        type(self._value),
                    )
                )



class MD5Field(BaseField):
    """
    Public: a field that stores an MD5 hash (as a str).
    """

    @staticmethod
    def parse(value):
        if hasattr(value, 'hexdigest'):
            value = value.hexdigest()
        return value

    def _type_validate(self):
        value = self._value
        is_valid = False
        if len(value) == 32:            
            try:
                int(value, 16)
            except ValueError:
                raise ValueError("%s's value (%s) is not a hex value" % (self.name, value))
            else:
                is_valid = True
        else:
            raise ValueError("%s's value (%s) is not 32 characters, as required by an MD5 hash" % (self.name, value))
        return is_valid



class UserIDField(BaseField):
    """
    Public: a field that stores a Django User ID (as an int if using the
            regular `id` property).

    The value is actually whatever the User model specifies as a primary key.
    The field can take a User model and will extract the primary key from it.
    """

    @staticmethod
    def parse(value):
        if hasattr(value, 'pk'):
            return value.pk
        return value



# We aren't doing much with the application_id right now beyond helping to keep
# experimental data segregated, so this doesn't actually do anything special.
class ApplicationIDField(BaseField):
    pass




class AnnotationListField(BaseField):
    def _type_validate(self):
        if self._value != None:
            if not isinstance(self._value, list):
                raise ValueError('%s must be a list, or None, got %s (%s)'% (self.name, self._value, type(self._value)))
            for v in self._value:
                if not isinstance(v, dict):
                    raise ValueError('Annotations must be dictionaries, got %s (%s)' % (v, type(v)))
                if not 'type' in v:
                    raise ValueError('Annotations must have a property `type`')
        return True



class ImageContentField(BaseField):
    def toJSONSafe(self, **kwargs):
        data = copy.deepcopy(self._value)
        return data

class ImageOriginalField(BaseField):
    def toJSONSafe(self, **kwargs):
        data = copy.deepcopy(self._value)
        return data



class ContainerContentField(BaseField):
    """
    Container content can be either a `list` of ContentIDs, or a `dict` of
    key–ContentID pairs, where the key is an arbitrary `str` value, or None.

    Content as a list:

        [
            '<type>:<uuid>',
            …
        ]

    …or as a dict:

        {
            'spam': '<type>:<uuid>',
            …
        }

    """

    @staticmethod
    def parse(value):
        if value:
            parsed = None
            if hasattr(value, 'iteritems'):
                parsed = {}
                for k, v in value.iteritems():
                    parsed[k] = ContentReferenceField.parse(v)
            elif hasattr(value, '__iter__'):
                parsed = map(ContentReferenceField.parse, value)
            if parsed != None:
                value = parsed
        return value

    def _type_validate(self):
        """Iterate over the provided value, ensuring that each member is a valid
        ContentID ('<type>:<uuid>'), or key–ContentID pair.
        """

        if self._value != None and not (isinstance(self._value, list) or isinstance(self._value, dict)):
            raise ValueError('%s must be a dict, list, or None, got %s (%s)'% (self.name, self._value, type(self._value)))
        if hasattr(self._value, 'values'):
            for v in self._value.values():
                _validateContentID(self.name, v)
        else:
            for v in self._value:
                _validateContentID(self.name, v)
        return True

    def toJSONSafe(self, full=False, **kwargs):
        """
        Public: provide a JSON-safe version of this field's value.

        full - (optional:False) Return one level of dereferenced content objects.

        """
        value = self._value
        if value:
            if hasattr(value, 'iteritems'):
                result = {}
                for k, v in value.iteritems():
                    v_output = ContentReferenceField().set(v).toJSONSafe(as_obj=True, dereference=full)
                    if value:
                        result[k] = v_output
            else:
                result = []
                for v in value:
                    v_output = ContentReferenceField().set(v).toJSONSafe(as_obj=True, dereference=full)
                    if v_output:
                        result.append(v_output)
            value = result
        return value



class ContentReferenceField(BaseField):
    @staticmethod
    def parse(value):
        from .models import instanceFromRaw
        if isinstance(value, basestring):
            value = {
                'id': value,
                'type': value.split(':')[0],
            }
        return instanceFromRaw(value)

    def _type_validate(self):
        value = self._value  
        return _validateContentID(self.name, self._value)

    def toJSONSafe(self, as_obj=False, dereference=False, **kwargs):
        """
        Public: provide a JSON-safe version of this field's value.

        Returns an ISO-format
        """

        value = self._value.toJSONSafe()
        return value


# use ContentIDField for .id, ContentReferenceField for .foo_content

# Like a ContentReferenceField, but only stores the raw ID property.
# Used as the .id property to avoid circular dereferencing.
class ContentIDField(BaseField):

    @staticmethod
    def parse(value):
        if hasattr(value, 'id'):
            value = value.id
        elif hasattr(value, 'get'):
            value = value.get('id', value)
        return value

    def _type_validate(self):
        value = self._value  
        return _validateContentID(self.name, self._value)

    def toJSONSafe(self, **kwargs):
        """
        Public: provide a JSON-safe version of this field's value.

        Returns an string ContentID.
        """
        value = self._value
        return value



def _validateContentID(field_name, value):
    from .models import ALL_TYPES
    if value != None:
        if not isinstance(value, basestring):
            raise ValueError('%s must be a valid ContentID, or None, got: %s' % (field_name, value))

        val = value.split(':')
        if len(val) != 2:
            raise ValueError("%s must be of format <type>:<uuid>, got: %s" % (field_name, value))
        type_val, uuid_val = val
        if not type_val in ALL_TYPES:
            raise ValueError("%s's type component (%s) must be one of %s" % (field_name, ALL_TYPES.keys()))
        try:
            UUID(uuid_val)
        except ValueError:
            raise ValueError("%s's UUID component (%s) is not a valid UUID" % (field_name, value))

    return True
