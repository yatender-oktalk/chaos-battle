defmodule ElixirChatWeb.UserSocket do
  use Phoenix.Socket

  # Channels
  channel "chat:*", ElixirChatWeb.ChatChannel

  def connect(%{"id" => user_id}, socket, _connect_info) do
    socket = assign(socket, :user_id, user_id)
    {:ok, socket}
  end

  def connect(_params, socket, _connect_info) do
    # Generate random user ID if not provided
    user_id = "user_#{:rand.uniform(1_000_000)}"
    socket = assign(socket, :user_id, user_id)
    {:ok, socket}
  end

  def id(socket), do: "user_socket:#{socket.assigns.user_id}"
end
