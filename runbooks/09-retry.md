# 09. Retry

[Previous](08-loop.md) · [Next](10-context.md)

## What and why

Retry the model request on HTTP 429 and 503. Honor `retry-after`, otherwise wait 2 seconds. Do not retry 400, 401, or 403. Do not run the tool again when the retry is the same request.

## Check

Three failed attempts raise `MaxRetriesExceeded`. A 401 fails on the first attempt.

## Ready code

`generate_with_retry` allows 2 retries (3 attempts) and only for status 429 and 503.
