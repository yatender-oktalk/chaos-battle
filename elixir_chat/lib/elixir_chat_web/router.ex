defmodule ElixirChatWeb.Router do
  use ElixirChatWeb, :router

  pipeline :api do
    plug(:accepts, ["json"])
  end

  scope "/", ElixirChatWeb do
    pipe_through(:api)

    get("/health", HealthController, :index)
    get("/stats", HealthController, :stats)
    get("/metrics", HealthController, :metrics)
  end
end
