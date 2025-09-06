![Scheduler Bind Type Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# Scheduler Bind Type in the BEAM VM (`+sbt` flag)

## What is the `+sbt` Flag?
The `+sbt` flag sets the scheduler thread binding strategy, controlling how schedulers are bound to CPU cores. This can affect performance on multi-core systems.

## Why is it Needed?
- Can improve cache locality and reduce context switching.
- Useful for tuning on NUMA or multi-socket systems.

## Example Usage
```sh
iex --erl "+sbt db" -S mix run --no-halt
```
- `+sbt db` enables dirty balancing.

## When to Tune?
- For advanced tuning on large servers or NUMA systems.
- Most users can leave this at the default.

## Drawbacks
- Incorrect settings can reduce performance.

## Summary
- Use `+sbt` for advanced scheduler/core binding.
- Only tune if you know your hardware topology.
