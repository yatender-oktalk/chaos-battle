import Config

# General configuration
config :elixir_chat,
  ecto_repos: []

# Phoenix endpoint configuration (NO ADAPTER SPECIFIED)
config :elixir_chat, ElixirChatWeb.Endpoint,
  url: [host: "localhost"],
  render_errors: [
    formats: [json: ElixirChatWeb.ErrorJSON],
    layout: false
  ],
  pubsub_server: ElixirChat.PubSub,
  live_view: [signing_salt: "random_signing_salt"]

# Phoenix configuration
config :phoenix, :json_library, Jason

# Logger configuration
config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

# Import environment specific config
import_config "#{config_env()}.exs"
