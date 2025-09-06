defmodule ElixirChat.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Raw ETS setup
      ElixirChat.RawApplication,
      # Raw Cowboy server ONLY (port 8081 - same as before)
      ElixirChat.RawServer
    ]

    opts = [strategy: :one_for_one, name: ElixirChat.Supervisor]
    Supervisor.start_link(children, opts)
  end

  @impl true
  def config_change(changed, _new, removed) do
    :ok
  end
end
