# xAOD Event Data Model Hints

Some hints to help with accessing xAOD objects.

## MissingET

Access:

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.MissingET().First()) \
    .Select(lambda m: {"met": m.met() / 1000.0'})
```

Despite being only a single missing ET for the event, it is stored as a sequence. Thus you must get the first object and then access the `.met()` method from there.
