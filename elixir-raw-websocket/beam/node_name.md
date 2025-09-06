![Node Name Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# Node Name in the BEAM VM (`-sname` / `-name` flags)

## What are the `-sname` and `-name` Flags?
These flags set the short or long node name for distributed Erlang/Elixir nodes, enabling communication between nodes.

## Why is it Needed?
- Required for distributed Erlang/Elixir (clustering, remote calls).

## Example Usage
```sh
iex --sname mynode
iex --name mynode@myhost
```
- `-sname` sets a short name (local network).
- `-name` sets a fully qualified name (for WAN).

## When to Tune?
- Always set when using distributed features.

## Drawbacks
- Node names must be unique in the cluster.
- Hostname resolution must work for `-name`.

## Summary
- Use `-sname`/`-name` for distributed BEAM nodes.
- Choose based on your network setup.
