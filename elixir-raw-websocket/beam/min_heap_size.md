![Min Heap Size Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# Minimum Heap Size in the BEAM VM (`+hms` flag)

## What is the `+hms` Flag?
The `+hms` flag sets the minimum heap size (in words) for BEAM processes. This can help performance for processes that need large heaps.

## Why is it Needed?
- Reduces the number of heap resizes for processes with large memory needs.
- Can improve performance for memory-intensive workloads.

## Example Usage
```sh
iex --erl "+hms 1024" -S mix run --no-halt
```
- `+hms 1024` sets the minimum heap size to 1024 words.

## When to Tune?
- For processes that frequently grow their heap.
- For high-performance or memory-intensive apps.

## Drawbacks
- Setting too high wastes memory for small processes.

## Summary
- Use `+hms` to tune minimum heap size for large processes.
- Set based on your workload's memory profile.
