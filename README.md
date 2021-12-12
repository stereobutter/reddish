# reddish - an redis client for sockets and trio with minimal api

* [Features](#features)
* [Installation](#installation)
* [Minimal Example](#minimal-example)
* [Usage](#usage)

## Features
* both sync and async API
* sync api using the standard library `socket` module (TPC, TPC+TLS, Unix domain sockets)
* `async`/`await` using `trio`'s stream primitives (TCP, TCP+TLS, Unix domain sockets)
* minimal api so you don't have to relearn how to write redis commands
* supports all redis commands including modules except `SUBSCRIBE`, `PSUBSCRIBE` and `MONITOR` [^footnote]
* parses responses back into python types if you like (powered by [pydantic](https://github.com/samuelcolvin/pydantic))
* works with every redis version and supports both `RESP2`and `RESP3` protocols

[^footnote]: Commands like `SUBSCRIBE` or `MONITOR` take over the redis connection for listeting to new events 
barring regular commands from being issued over the connection. 

## Installation
```
pip install reddish  # install just with support for socket
pip install reddish[trio]  # install with support for trio
```

## Minimal Example - sync version
```python
import socket
from reddish.socket import Redis, Command

redis = Redis(socket.create_connection(('localhost', 6379)))

assert b'PONG' == redis.execute(Command('PING'))
```

## Minimal Example - async version
```python
import trio
from reddish.trio import Redis, Command

redis = Redis(await trio.open_tcp_stream('localhost', 6379))

assert b'PONG' == await redis.execute(Command('PING'))
```

## Usage

### Command with a fixed number of arguments
```python
# simple command without any arguments
Command('PING')

# commands with positional arguments
Command('ECHO {}', 'hello world')

# commands with keyword arguments
Command('SET {key} {value}', key='foo', value=42)
```

### Command with response parsing
```python
# return response unchanged from redis
assert b'42' == await redis.execute(Command('ECHO {}', 42))

# parse response as type
assert 42 == await redis.execute(Command('ECHO {}', 42).into(int))

# use any type that works with pydantic
from pydantic import Json
import json

data = json.dumps({'alice': 30, 'bob': 42})
response == await redis.execute(Command('ECHO {}', data).into(Json))
assert response == json.loads(data)
```

### Command with variadic arguments
```python
from reddish.trio import Args

# inlining arguments
Command('DEL {keys}', keys=Args(['foo', 'bar']))  # DEL foo bar

# inlining pairwise arguments 
data = {'name': 'bob', 'age': 42}
Command('XADD foo * {fields}', fields=Args.from_dict(data))  # XADD foo * name bob age 42
``` 

### Pipelining commands
```python
foo, bar = await redis.execute_many(Command('GET', 'foo'), Command('GET', 'bar'))
```

### Transactions
```python
from reddish.trio import MultiExec

tx = MultiExec(
    Command('ECHO {}', 'foo'),
    Command('ECHO {}', 'bar')
)

foo, bar = await redis.execute(tx)

# pipelining together with transactions
[foo, bar], baz = await redis.execute_many(tx, Command('ECHO {}', 'baz'))
```
