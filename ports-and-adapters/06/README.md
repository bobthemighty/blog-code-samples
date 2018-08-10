To run the code, set up a python 3 virtual environment, then

`pip install -r requirements.txt`
`pip install -e .`

You will need Sqlite installed. For the API, you'll need write-access to the current directory, or you can just hack the connection string in adapters/flask.py


## running the quick tests

```bash
run-contexts issues/slow_tests
```

## running the slow tests

First, run the API flask app in a separate terminal:

```bash
python -m issues.adapters.flask
```

Then, run:

```bash
run-contexts issues/slow_tests
```


# To run the API

```bash
$ python -m issues.adapters.flask
 flask run
 * Serving Flask app "issues.adapters.flask"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
127.0.0.1 - - [13/Sep/2017 13:50:50] "POST /issues HTTP/1.1" 201 -
127.0.0.1 - - [13/Sep/2017 13:50:57] "GET /issues/4d9ca3ab-3d70-486c-965b-41d27e0dbd33 HTTP/1.1" 200 -
```

You can now post a new issue to the api.

```bash
$ curl -d'{"reporter_name": "carlos", "reporter_email": "carlos@example.org", "problem_description": "Nothing works any more"}' localhost:5000/issues -H "Content-Type: application/json" -v

*   Trying ::1...
* TCP_NODELAY set
* connect to ::1 port 5000 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 5000 (#0)
> POST /issues HTTP/1.1
> Host: localhost:5000
> User-Agent: curl/7.55.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 108
> 
* upload completely sent off: 108 out of 108 bytes
* HTTP 1.0, assume close after body
< HTTP/1.0 201 CREATED
< Location: http://localhost:5000/issues/4d9ca3ab-3d70-486c-965b-41d27e0dbd33
< Content-Type: text/html; charset=utf-8
< Content-Length: 0
< Server: Werkzeug/0.12.2 Python/3.6.2
< Date: Wed, 13 Sep 2017 12:50:50 GMT
< 
* Closing connection 0

```


And fetch the new issue from the URI given in the Location header.

```bash
curl http://localhost:5000/issues/4d9ca3ab-3d70-486c-965b-41d27e0dbd33
{
  "description": "Nothing works any more", 
  "reporter_email": "carlos@example.org", 
  "reporter_name": "carlos"
}
```
