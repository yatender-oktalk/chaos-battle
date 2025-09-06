defmodule ElixirRawChat.MixProject do
  use Mix.Project

  def project do
    [
      app: :elixir_raw_chat,
      version: "0.1.0",
      elixir: "~> 1.18",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      mod: {ElixirRawChat.Application, []},
      extra_applications: [:logger]
    ]
  end

  defp deps do
    [
      {:cowboy, "~> 2.10"},
      {:jason, "~> 1.2"},
      {:observer_cli, "~> 1.7"}
    ]
  end
end
