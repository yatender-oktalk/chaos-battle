defmodule ElixirRawChatTest do
  use ExUnit.Case
  doctest ElixirRawChat

  test "greets the world" do
    assert ElixirRawChat.hello() == :world
  end
end
