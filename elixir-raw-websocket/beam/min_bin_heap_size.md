![Min Bin Heap Size Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# Minimum Binary Heap Size in the BEAM VM (`+hmbs` flag)

## What is the `+hmbs` Flag?
The `+hmbs` flag sets the minimum binary heap size for BEAM processes. This is useful for processes that handle large binaries.

## Why is it Needed?
- Reduces binary heap resizes for processes working with large binaries.
- Can improve performance for binary-heavy workloads.


## Example Usage
```sh
iex --erl "+hmbs 1024" -S mix run --no-halt
```
- `+hmbs 1024` sets the minimum binary heap size to 1024 words.

## Sample Elixir Code
Here's a simple example that allocates large binaries in a loop. You can observe memory usage and performance with different `+hmbs` values:

```elixir
defmodule BinHeapDemo do
	def run(n, size) do
		for _ <- 1..n do
			# Allocate a binary of given size (in bytes)
			:crypto.strong_rand_bytes(size)
		end
	end
end

# Run with:
# BinHeapDemo.run(100_000, 2048)
```

Try running this with and without `+hmbs 1024` to see the effect on memory usage and GC.

## Diagram: Binary Heap Growth

```
Process Start
	 |
	 |--[allocates small binary]---> [small bin heap]
	 |--[allocates large binary]---> [bin heap grows]
	 |--[many large binaries]------> [bin heap resizes often]
	 |
	 |--[+hmbs set large enough]---> [bin heap starts big, fewer resizes]
```

Setting `+hmbs` high enough for your workload can reduce the number of binary heap resizes, improving performance for binary-heavy processes.

## When to Tune?
- For processes that frequently allocate large binaries.

## Drawbacks
- Setting too high wastes memory for small processes.

## Summary
- Use `+hmbs` to tune binary heap size for binary-heavy processes.
- Set based on your workload's binary usage.
