---
name: current_time
track: bonus
kind: local_formatter
provider: Python zoneinfo
requires_env: []
inputs: [timezone]
outputs: [iso, date, weekday, timezone]
side_effect: false
---
# current_time

Returns the current date/time in an IANA timezone (default `Asia/Ho_Chi_Minh`).
Use only when the user asks what time/date/weekday it is now. Unknown or
empty timezones return an error dict instead of raising.
