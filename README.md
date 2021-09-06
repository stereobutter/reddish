# reddish - an async redis client with minimal api

* [Features](#Features)
* [Installation](#Installation)
* [Usage](#Usage)

## Features
* `async`/`await` using `trio`
* minimal, command oriented api so you don't have to relearn writing redis commands
* supports all request/reply redis commands (including modules)
* easy pipelining of commands and transactions
* optional serialization of common python types e.g. `dict`, `list`, `datetime` etc. to json
* optional parsing of responses back into python types (powered by [pydantic](https://github.com/samuelcolvin/pydantic))
* supports both `RESP2` and `RESP3` redis protocols
* supports TCP, TCP+TLS and Unix domain sockets using the respective `trio.Stream`

## Installation
```
pip install reddish
```

## Usage

### Executing commands
```python
from reddish import Redis, Command

redis = Redis(await trio.open_tcp_stream('localhost', 6379))

# execute single redis command
foo = await redis.execute(Command('GET', 'foo'))

# execute multiple redis commands at once
foo = await redis.execute(Command('GET', 'foo'), Command('GET', 'bar'))
```

### Transactions
```python
from reddish import MultiExec

# pipeline multiple commands and execute some of them using a redis transaction
[bar, baz], zap = await redis.execute(
    MultiExec(
        Command('SET', 'bar', 1),
        Command('SET', 'baz', 2)
        )
    Command('GET', 'zap')
    )
```

### Serialization and encoding of common python types
```python
 # serialize python objects to json and encode using UTF-8
await redis.execute(Command('SET', 'foo', dict(a=1, b=2)))  # b'{"a":1, "b":2}'
```

### Parsing data back into python types
```python
# execute redis command and parse the response into a given type
foo = await redis.execute(Command('GET', 'foo').into(dict[str, int]))
```