# BEAST MODE configuration
config :elixir_raw_chat, ElixirRawChat.Endpoint,
  http: [
    port: 8081,
    protocol_options: [
      max_connections: 4_000_000,
      num_acceptors: 2000,
      max_keepalive: 10_000_000,
      timeout: 60_000,
      compress: false,
      idle_timeout: 300_000,
      inactivity_timeout: 600_000,
      max_frame_size: 262_144,
      max_frame_size: 1_048_576
    ]
  ]

# Optimize GenServer calls
config :logger,
  # Minimal logging for max performance
  level: :error,
  # Disable all backends for ultimate speed
  backends: []

# Optimize for memory
config :elixir, :ansi_enabled, false
