# Battery Python API library

[![PyPI version](https://img.shields.io/pypi/v/Battery.svg)](https://pypi.org/project/Battery/)

The Battery Python library provides convenient access to the Battery REST API from any Python 3.7+
application. The library includes type definitions for all request params and response fields,
and offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx).

## Documentation

The REST API documentation can be found Battery Docs, will be available soon. The full API of this library can be found in [api.md](api.md).

## Installation

```sh
# install from PyPI
pip install Battery
```

## Usage

The full API of this library can be found in [api.md](api.md).

```python
import os
from Battery import Battery

client = Battery(
    # This is the default and can be omitted
    api_key=os.environ.get("Battery_API_KEY"),
)

eval = client.evaluation.create(
    input="Is it legal to monitor employee emails under European privacy laws?",
    metrics=["precision", "recall"],
    response="Monitoring employee emails is permissible under European privacy laws like GDPR, provided there's a legitimate purpose.",
    context="European privacy laws, including GDPR, allow for the monitoring of employee emails under strict conditions. The employer must demonstrate that the monitoring is necessary for a legitimate purpose, such as protecting company assets or compliance with legal obligations. Employees must be informed about the monitoring in advance, and the privacy impact should be assessed to minimize intrusion.",
)
print(f"Precision score {eval.evaluations['precision'].score} / 5")
```

While you can provide an `api_key` keyword argument,
we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/)
to add `Battery_API_KEY="My API Key"` to your `.env` file
so that your API Key is not stored in source control.

## Async usage

Simply import `AsyncBattery` instead of `Battery` and use `await` with each API call:

```python
import os
import asyncio
from Battery import AsyncBattery

client = AsyncBattery(
    # This is the default and can be omitted
    api_key=os.environ.get("Battery_API_KEY"),
)


async def main() -> None:
    eval = await client.evaluation.create(
        input="Is it legal to monitor employee emails under European privacy laws?",
        metrics=["precision", "recall"],
        response="Monitoring employee emails is permissible under European privacy laws like GDPR, provided there's a legitimate purpose.",
        context="European privacy laws, including GDPR, allow for the monitoring of employee emails under strict conditions. The employer must demonstrate that the monitoring is necessary for a legitimate purpose, such as protecting company assets or compliance with legal obligations. Employees must be informed about the monitoring in advance, and the privacy impact should be assessed to minimize intrusion.",
    )
    print(f"Precision score {eval.evaluations['precision'].score} / 5")


asyncio.run(main())
```

Functionality between the synchronous and asynchronous clients is otherwise identical.

## Using types

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into JSON, `model.to_json()`
- Converting to a dictionary, `model.to_dict()`

Typed requests and responses provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `basic`.

## Handling errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `Battery.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx
response), a subclass of `Battery.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `Battery.APIError`.

```python
import Battery
from Battery import Battery

client = Battery()

try:
    client.evaluation.create(
        input="Is it legal to monitor employee emails under European privacy laws?",
        metrics=["precision", "recall"],
        response="Monitoring employee emails is permissible under European privacy laws like GDPR, provided there's a legitimate purpose.",
        context="European privacy laws, including GDPR, allow for the monitoring of employee emails under strict conditions. The employer must demonstrate that the monitoring is necessary for a legitimate purpose, such as protecting company assets or compliance with legal obligations. Employees must be informed about the monitoring in advance, and the privacy impact should be assessed to minimize intrusion.",
    )
except Battery.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except Battery.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except Battery.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error codes are as followed:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

### Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,
429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
from Battery import Battery

# Configure the default for all requests:
client = Battery(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).evaluation.create(
    input="Is it legal to monitor employee emails under European privacy laws?",
    metrics=["precision", "recall"],
    response="Monitoring employee emails is permissible under European privacy laws like GDPR, provided there's a legitimate purpose.",
    context="European privacy laws, including GDPR, allow for the monitoring of employee emails under strict conditions. The employer must demonstrate that the monitoring is necessary for a legitimate purpose, such as protecting company assets or compliance with legal obligations. Employees must be informed about the monitoring in advance, and the privacy impact should be assessed to minimize intrusion.",
)
```

### Timeouts

By default requests time out after 1 minute. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/#fine-tuning-the-configuration) object:

```python
from Battery import Battery

# Configure the default for all requests:
client = Battery(
    # 20 seconds (default is 1 minute)
    timeout=20.0,
)

# More granular control:
client = Battery(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5.0).evaluation.create(
    input="Is it legal to monitor employee emails under European privacy laws?",
    metrics=["precision", "recall"],
    response="Monitoring employee emails is permissible under European privacy laws like GDPR, provided there's a legitimate purpose.",
    context="European privacy laws, including GDPR, allow for the monitoring of employee emails under strict conditions. The employer must demonstrate that the monitoring is necessary for a legitimate purpose, such as protecting company assets or compliance with legal obligations. Employees must be informed about the monitoring in advance, and the privacy impact should be assessed to minimize intrusion.",
)
```

On timeout, an `APITimeoutError` is thrown.

Note that requests that time out are [retried twice by default](#retries).

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals)_.
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/Battery-ai/Battery-sdk-python/issues) with questions, bugs, or suggestions.

## Requirements

Python 3.7 or higher.
