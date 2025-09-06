![ETS Table Limit Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# ETS Table Limit in the BEAM VM (`+e` flag)

## What is the `+e` Flag?
The `+e` flag sets the maximum number of ETS (Erlang Term Storage) tables that can be created in the BEAM VM.

## Why is it Needed?
- Allows tuning for apps that need many ETS tables (e.g., large caches, sharded data).

## Example Usage
```sh
iex --erl "+e 50000" -S mix run --no-halt
```
- `+e 50000` allows up to 50,000 ETS tables.

## When to Tune?
- For apps that create many ETS tables.
- Default is usually 1,400; increase only if needed.

## Drawbacks
- Setting too high can increase memory usage.

## Summary
- Use `+e` to raise the ETS table limit for large-scale apps.
- Monitor memory and table usage.
