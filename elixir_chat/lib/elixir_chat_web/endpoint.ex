defmodule ElixirChatWeb.Endpoint do
  use Phoenix.Endpoint, otp_app: :elixir_chat

  # WebSocket configuration optimized for high load
  socket "/socket", ElixirChatWeb.UserSocket,
    websocket: [
      timeout: 45_000,
      max_frame_size: 4_194_304,
      compress: false,
      idle_timeout: 60_000
    ],
    longpoll: false

  # Serve at "/" the static files from "priv/static" directory.
  plug Plug.Static,
    at: "/",
    from: :elixir_chat,
    gzip: false,
    only: ElixirChatWeb.static_paths()

  # HTTP configuration (minimal - no telemetry overhead)
  plug Plug.RequestId

  plug Plug.Parsers,
    parsers: [:urlencoded, :multipart, :json],
    pass: ["*/*"],
    json_decoder: Phoenix.json_library()

  plug Plug.MethodOverride
  plug Plug.Head
  plug ElixirChatWeb.Router
end
