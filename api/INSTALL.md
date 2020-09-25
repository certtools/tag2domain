# How to install the API

1. make sure you have all the python packages you need installed:

```
pip install -r requirements.txt
```

2. make sure you know which DB to connect to and how to connect to it: edit the file ``ENV``.
3. ``source ENV``
4. edit config.py and adapt to your needs
5. Start uvicorn:

```
uvicorn --reload main:app
```

6. test it: go to $baseurl/docs. You might need to acquire an API key first. See ``db/api_keys.sql``. 


