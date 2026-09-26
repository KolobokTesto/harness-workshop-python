# 04. Tools

[Previous](03-function.md) · [Next](05-call.md)

## What and why

Describe `searchStories`, `readDiscussion`, and `saveDigest` with Pydantic models. The model can see the schemas. Nothing runs them yet.

## Check

Schemas reject a non-string query and an empty digest. They accept `{"query": "harness"}`.

## Ready code

`src/news/agent.py` builds Claude tool dicts (`name`, `description`, `input_schema`) from `SearchInput`, `DiscussionInput`, and `DigestInput`.
