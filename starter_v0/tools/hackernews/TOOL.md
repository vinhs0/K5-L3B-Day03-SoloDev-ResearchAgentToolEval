---
name: hackernews
track: bonus
kind: live_api
provider: Hacker News (Algolia)
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# hackernews

Searches Hacker News stories via the public Algolia API. `sort` is `relevance`
or `date`. Only for when the user explicitly mentions Hacker News / HN; general
news goes to `lookup`. `limit` is clamped to 1..20. Errors come back as an
error dict.
