![Env Var Cover](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=1000&q=80)

# Environment Variables in the BEAM VM (`-env` flag)

## What is the `-env` Flag?
The `-env` flag sets an environment variable for the BEAM VM at startup.

## Why is it Needed?
- Used to configure the VM or application at launch.

## Example Usage
```sh
iex --env VAR value -S mix run --no-halt
```
- `-env VAR value` sets the environment variable `VAR` to `value`.

## When to Tune?
- Whenever you need to set environment variables for your app or the VM.

## Drawbacks
- None specific to the flag; depends on the variable set.

## Summary
- Use `-env` to set environment variables at VM startup.
- Useful for configuration and secrets.
