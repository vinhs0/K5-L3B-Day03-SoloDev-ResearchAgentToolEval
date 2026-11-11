---
name: wikipedia
track: bonus
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [title, lang]
outputs: [items]
side_effect: false
---
# wikipedia

Fetches the encyclopedic summary of ONE Wikipedia article by title. Use for
background/definition questions ("X là gì?", "who is Y"). Not for breaking
news (use `lookup`). Returns an error dict when the title is empty, the
language is unsupported, or the page does not exist.
