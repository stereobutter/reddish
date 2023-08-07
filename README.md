# reddish - a friendly redis client with sync and async api

[![PyPI](https://img.shields.io/pypi/v/reddish?color=blue)](https://pypi.org/project/reddish/)
[![Build Status](https://shields.io/github/workflow/status/stereobutter/reddish/linting_and_testing)](https://github.com/stereobutter/reddish/actions/workflows/linting_and_testing.yml/)

* [Features](#features)
* [Installation](#installation)
* [Minimal Example](#minimal-example)
* [Usage](#usage)

## Features
* both sync and async API
* sync api using the standard library `socket` module (TPC, TPC+TLS, Unix domain sockets)
* `async`/`await` using `asyncio`'s, `trio`'s or `anyio`'s stream primitives (TCP, TCP+TLS, Unix domain sockets)
* minimal api so you don't have to relearn how to write redis commands
* supports all redis commands including modules except `SUBSCRIBE`, `PSUBSCRIBE` and `MONITOR` [^footnote]
* parses responses back into python types if you like (powered by [pydantic](https://github.com/samuelcolvin/pydantic))
* works with every redis version and supports both `RESP2`and `RESP3` protocols

[^footnote]: Commands like `SUBSCRIBE` or `MONITOR` take over the redis connection for listeting to new events 
barring regular commands from being issued over the connection. 

## Installation
```
pip install reddish  # install just with support for socket and asyncio
pip install reddish[trio]  # install with support for trio
pip install reddish[anyio]  # install with support for anyio
```

## Minimal Example - sync version
```python
import socket
from reddish import Command
from reddish.backends.socket import Redis

redis = Redis(socket.create_connection(('localhost', 6379)))

assert b'PONG' == redis.execute(Command('PING'))
```

## Minimal Example - async version (asyncio)
```python
import asyncio
from reddish.backends.asyncio import Redis

redis = Redis(await asyncio.open_connection('localhost', 6379))

assert b'PONG' == await redis.execute(Command('PING'))
```

## Minimal Example - async version (trio)
```python
import trio
from reddish.backends.trio import Redis

redis = Redis(await trio.open_tcp_stream('localhost', 6379))

assert b'PONG' == await redis.execute(Command('PING'))
```

## Minimal Example - async version (anyio)
```python
import trio
from reddish.backends.anyio import Redis

redis = Redis(await anyio.connect_tctp('localhost', 6379))

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

### Catching invalid commands
```python
from reddish import CommandError

try:
    await redis.execute(Command("foo"))
except CommandError as error:
    print(error.message)  # >>> ERR unknown command `foo`, with args beginning with:
```

### Command with response parsing
```python
# return response unchanged from redis
assert b'42' == await redis.execute(Command('ECHO {}', 42))

# parse response as type
assert 42 == await redis.execute(Command('ECHO {}', 42).into(int))

# handling replies that won't parse correctly
from reddish import ParseError

try:
    await redis.execute(Command('PING').into(int))
except ParseError as error:
    print(error.reply)

# use any type that works with pydantic
from pydantic import Json
import json

data = json.dumps({'alice': 30, 'bob': 42})
response == await redis.execute(Command('ECHO {}', data).into(Json))
assert response == json.loads(data)
```

### Command with variadic arguments
```python
from reddish import Args

# inlining arguments
Command('DEL {keys}', keys=Args(['foo', 'bar']))  # DEL foo bar

# inlining pairwise arguments 
data = {'name': 'bob', 'age': 42}
Command('XADD foo * {fields}', fields=Args.from_dict(data))  # XADD foo * name bob age 42
``` 

### Pipelining commands
```python
foo, bar = await redis.execute_many(Command('GET', 'foo'), Command('GET', 'bar'))

# handling errors in a pipeline
from reddish import PipelineError

try:
    foo, bar = await redis.execute_many(*commands)
except PipelineError as error:
    for outcome in error.outcomes:
        try:
            # either returns the reply if it was successful 
            # or raises the original exception if not
            value = outcome.unwrap() 
            ...
        except CommandError:
            ...
        except ParseError:
            ...
```

### Transactions
```python
from reddish import MultiExec

tx = MultiExec(
    Command('ECHO {}', 'foo'),
    Command('ECHO {}', 'bar')
)

foo, bar = await redis.execute(tx)

# handling errors with transactions
try:
    await redis.execute(some_tx)
except CommandError as error:
    # The exception as a whole failed and redis replied with an EXECABORT error
    cause = error.__cause__  # original CommandError that caused the EXECABORT
    print(f'Exception aborted due to {cause.code}:{cause.message}')
except TransactionError as error:
    # Some command inside the transaction failed 
    # but the transaction as a whole succeeded
    # to get at the partial results of the transaction and the errors 
    # you can iterate over the outcomes of the transaction
    for outcome in error.outcomes:
        try:
            outcome.unwrap()  # get the value or raise the original error
        except CommandError:
            ...
        except ParseError:
            ...


# pipelining together with transactions
[foo, bar], baz = await redis.execute_many(tx, Command('ECHO {}', 'baz'))

# handling errors with transactions inside a pipeline
try:
    res: list[int] = await redis.execute_many(*cmds)
except PipelineError as error:
    # handle the outcomes of the pipeline
    for outcome in error.outcomes:
        try:
            outcome.unwrap()
        except CommandError:
            ...
        except ParseError:
            ...
        except TransactionError as tx_error:
            # handle errors inside the transaction
            for tx_outcome in tx_error.outcomes:
                ...
```