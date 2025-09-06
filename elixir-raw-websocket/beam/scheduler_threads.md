![Scheduler Threads Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# Scheduler Threads in the BEAM VM (`+S` flag)

## What is the `+S` Flag?
The `+S` flag sets the number of scheduler threads (OS threads) used by the BEAM VM. Each scheduler thread runs BEAM processes and maps to a CPU core.

## Why is it Needed?
- Controls how many CPU cores the BEAM VM uses for running processes.
- More schedulers = more parallelism, up to the number of physical/logical cores.


## Example Usage
```sh
iex --erl "+S 8" -S mix run --no-halt
```
- `+S 8` uses 8 scheduler threads (good for 8-core CPUs).

## Sample Elixir Code
Here's a simple example that runs CPU-bound tasks. Try with different `+S` values and observe CPU usage:

```elixir
defmodule SchedulerDemo do
	def run(n) do
		tasks = for _ <- 1..n do
			Task.async(fn -> Enum.sum(1..10_000_000) end)
		end
		Enum.each(tasks, &Task.await(&1, 10_000))
	end
end

# Run with:
# SchedulerDemo.run(8)
```

## Diagram: Scheduler Threads

```
BEAM VM
	|
	|--[Scheduler 1] (CPU core 1)
	|--[Scheduler 2] (CPU core 2)
	|-- ...
	|--[Scheduler N] (CPU core N)
```

The number of schedulers determines parallelism.

## When to Tune?
- Set to the number of available CPU cores for best performance.
- For most workloads, match the number of schedulers to the number of cores.

## Drawbacks
- Setting too high can cause context switching overhead.
- Setting too low underutilizes hardware.

## Summary
- Use `+S` to control BEAM parallelism.
- Match to your CPU core count for optimal performance.
