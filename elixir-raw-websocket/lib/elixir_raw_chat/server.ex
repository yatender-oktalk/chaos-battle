# Focus on application-level optimizations
defmodule ElixirRawChat.Server do
  def child_spec(_) do
    routes = [
      {"/ws/:user_id", ElixirRawChat.WebSocketHandler, []},
      {"/ws", ElixirRawChat.WebSocketHandler, []},
      {"/health", ElixirRawChat.HealthHandler, []},
      {"/stats", ElixirRawChat.StatsHandler, []}
    ]

    dispatch = :cowboy_router.compile([{:_, routes}])

    # MAXED OUT for macOS
    cowboy_opts = %{
      env: %{dispatch: dispatch},
      max_connections: 1_000_000,
      # AGGRESSIVE for macOS
      num_acceptors: 800,
      max_keepalive: 10_000,
      # Shorter timeout
      timeout: 30_000,
      compress: false,
      inactivity_timeout: 300_000,
      max_frame_size: 131_072,
      # Faster cleanup
      idle_timeout: 30_000
    }

    # macOS-optimized socket settings
    ranch_opts = %{
      socket_opts: [
        {:port, 8081},
        {:ip, {0, 0, 0, 0}},
        {:nodelay, true},
        # Shorter timeout
        {:send_timeout, 3000},
        {:send_timeout_close, true},
        # Conservative for macOS
        {:backlog, 8192},
        {:reuseaddr, true},
        {:keepalive, true},
        # Reasonable for macOS
        {:buffer, 65536},
        {:sndbuf, 65536},
        {:recbuf, 65536}
      ],
      max_connections: 1_000_000,
      num_acceptors: 800
    }

    %{
      id: __MODULE__,
      start: {:cowboy, :start_clear, [:raw_websocket_server, ranch_opts, cowboy_opts]},
      type: :worker,
      restart: :permanent
    }
  end
end
