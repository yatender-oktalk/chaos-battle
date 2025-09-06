![SMP Threads Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# SMP Threads in the BEAM VM (`+T` flag)

## What is the `+T` Flag?
The `+T` flag sets the number of threads for SMP (Symmetric Multi-Processing) support in the BEAM VM. It is rarely needed for most users, as the VM auto-detects cores.

## Why is it Needed?
- For advanced tuning of thread pools in SMP mode.
- Most users do not need to set this manually.

## Example Usage
```sh
iex --erl "+T 4" -S mix run --no-halt
```
- `+T 4` sets 4 SMP threads.

## When to Tune?
- Only for advanced scenarios or debugging.

## Drawbacks
- Incorrect values can reduce performance or cause instability.

## Summary
- Use `+T` for advanced SMP thread tuning.
- Usually, let the BEAM VM auto-detect core/thread count.
