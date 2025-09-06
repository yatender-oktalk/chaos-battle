import Config

config :elixir_chat, ElixirChatWeb.Endpoint,
  http: [
    port: 8081,
    protocol_options: [
      max_connections: 200_000,
      max_keepalive: 5000,
      timeout: 60_000,
      num_acceptors: 500        # Reduce from 1000 to 500
    ]
  ],
  server: true,
  check_origin: false

config :phoenix, :json_library, Jason

# DISABLE problematic logging to prevent crashes
config :logger, level: :error  # Only errors, no warnings
config :logger, :console,
  format: "$message\n",
  metadata: []

# Disable Ranch logging specifically
config :ranch, log_level: :error
