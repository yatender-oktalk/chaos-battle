import Config

config :elixir_chat, ElixirChatWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 8081],
  check_origin: false,
  code_reloader: true,
  debug_errors: true,
  secret_key_base: "very_long_secret_key_base_for_development_only_not_for_production_use_must_be_64_chars",
  watchers: []

config :logger, level: :debug
