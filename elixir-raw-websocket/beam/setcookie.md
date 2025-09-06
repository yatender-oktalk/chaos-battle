![Setcookie Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# Setcookie in the BEAM VM (`-setcookie` flag)

## What is the `-setcookie` Flag?
The `-setcookie` flag sets the cookie value for distributed Erlang/Elixir nodes, used for authentication between nodes.

## Why is it Needed?
- Required for secure communication between nodes.

## Example Usage
```sh
iex --sname mynode --setcookie mysecret
```
- `-setcookie mysecret` sets the cookie value.

## When to Tune?
- Always set when using distributed features.

## Drawbacks
- All nodes must use the same cookie value.
- Exposing the cookie can be a security risk.

## Summary
- Use `-setcookie` for distributed node authentication.
- Keep your cookie value secret.
