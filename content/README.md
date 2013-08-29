py-content
==========

Create an API wrapper instance for a specific user:

```python
>>> co = ContentObjects(CONTENT_API_TOKEN)
```


Get all objects owned by the authenticated user:

```python
>>> co.all()
```

    
Retrieve a listing of object, filtered by parameters:

```python
>>> co.filter(content=some_id)
>>> co.filter(type=Text)
>>> # Can also use a string, but the class is preferred
>>> co.filter(type='text')
```


Retrieve a specific object by id:

```python
>>> obj = co.fetch(obj_id)
```


Create a new Text object:

```
>>> text_obj = co.create(Text, obj_attrs)
```

Modify and save the text object:

```python
>>> text_obj.content = 'New content'
>>> # Or more than one at a time (like a dictionary)
>>> text_obj.update({
...         'content'   : 'New content',
...         'role'      : 'quote',
...     })
>>> co.save(text_obj)
```

Or save a whole bunch of objects:

```python
>>> co.save(obj1, obj2, obj3)
>>> co.save([obj1, obj2, obj3])
```

Add an annotation:

```python
>>> text_obj.annotations = [{
...         'type'  : 'link',
...         'start' : 0,
...         'end'   : 3,
...         'url'   : 'http://example.com',
...     }]
>>> text_obj.content
u'New content'
>>> text_obj.toHTML()
u'<a href="http://example.com">New</a> content'
```
