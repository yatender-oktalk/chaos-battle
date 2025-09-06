defmodule ElixirChat.MixProject do
  use Mix.Project

  def project do
    [
      app: :elixir_chat,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      mod: {ElixirChat.Application, []},
      extra_applications: [:logger, :runtime_tools]
    ]
  end

  defp deps do
    [
      # RAW WebSocket dependencies ONLY
      {:cowboy, "~> 2.10"},
      {:jason, "~> 1.2"}
    ]
  end
end
