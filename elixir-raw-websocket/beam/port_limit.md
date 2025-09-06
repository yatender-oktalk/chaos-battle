![Port Limit Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# Port Limit in the BEAM VM (`+Q` flag)

## What is the `+Q` Flag?
The `+Q` flag sets the maximum number of ports (external resources like sockets, files, etc.) the BEAM VM can open. Each port represents a connection to the outside world.

## Why is it Needed?
- Prevents the VM from opening too many sockets/files and exhausting OS resources.
- Allows tuning for high-connection workloads (e.g., websocket servers).


## Example Usage
```sh
iex --erl "+Q 1000000" -S mix run --no-halt
```
- `+Q 1000000` allows up to 1 million ports.

## Sample Elixir Code
Here's a simple example that opens many ports (TCP sockets). Try with different `+Q` values:

```elixir
defmodule PortLimitDemo do
	def run(n) do
		for _ <- 1..n do
			{:ok, _} = :gen_tcp.listen(0, [])
		end
	end
end

# Run with:
# PortLimitDemo.run(1000)
```

## Diagram: Port Table

```
BEAM VM
	|
	|--[Port 1]
	|--[Port 2]
	|-- ...
	|--[Port N] (limited by +Q)
```

The port table size is capped by the `+Q` flag.

## When to Tune?
- Increase for apps with many concurrent sockets/files.
- Default is usually 65,536; increase only if you need more.

## Drawbacks
- Setting too high can hit OS-level limits (ulimit -n).
- Monitor OS and VM resource usage.

## Summary
- Use `+Q` to raise the port limit for high-connection apps.
- Ensure OS limits are also increased accordingly.
