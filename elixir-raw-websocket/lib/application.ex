defmodule ElixirRawChat.Application do
  use Application

  @impl true
  def start(_type, _args) do
    # Create ETS tables for connection tracking
    :ets.new(:connections, [
      :set,
      :public,
      :named_table,
      {:read_concurrency, true},
      {:decentralized_counters, true}
    ])

    :ets.new(:stats, [
      :set,
      :public,
      :named_table,
      {:write_concurrency, true},
      {:decentralized_counters, true}
    ])

    # Initialize stats
    :ets.insert(:stats, {:connections, 0})
    :ets.insert(:stats, {:messages, 0})

    children = [
      # Start the raw WebSocket server
      ElixirRawChat.Server
    ]

    opts = [strategy: :one_for_one, name: ElixirRawChat.Supervisor]

    IO.puts("🔥 RAW ELIXIR WEBSOCKET SERVER STARTING")
    IO.puts("⚡ WebSocket: ws://localhost:8081/ws/user123")
    IO.puts("📊 Stats: http://localhost:8081/stats")
    IO.puts("💪 Health: http://localhost:8081/health")

    Supervisor.start_link(children, opts)
  end

  @impl true
  def config_change(_changed, _new, _removed) do
    :ok
  end
end
