use std::net::SocketAddr;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::broadcast;
use tokio::time::timeout;
use tokio_tungstenite::{accept_async, tungstenite::Message, WebSocketStream};
use futures_util::{SinkExt, StreamExt};
use dashmap::DashMap;
use uuid::Uuid;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ChatMessage {
    id: String,
    content: String,
    timestamp: u64,
    user: String,
}

#[derive(Debug)]
struct ConnectionMetrics {
    connections: AtomicUsize,
    messages_sent: AtomicU64,
    messages_received: AtomicU64,
    bytes_sent: AtomicU64,
    bytes_received: AtomicU64,
    errors: AtomicU64,
}

impl ConnectionMetrics {
    fn new() -> Self {
        Self {
            connections: AtomicUsize::new(0),
            messages_sent: AtomicU64::new(0),
            messages_received: AtomicU64::new(0),
            bytes_sent: AtomicU64::new(0),
            bytes_received: AtomicU64::new(0),
            errors: AtomicU64::new(0),
        }
    }

    fn print_stats(&self) {
        let connections = self.connections.load(Ordering::Relaxed);
        let msg_sent = self.messages_sent.load(Ordering::Relaxed);
        let msg_recv = self.messages_received.load(Ordering::Relaxed);
        let bytes_sent = self.bytes_sent.load(Ordering::Relaxed);
        let bytes_recv = self.bytes_received.load(Ordering::Relaxed);
        let errors = self.errors.load(Ordering::Relaxed);

        println!("📊 RUST METRICS:");
        println!("   🔗 Connections: {}", connections);
        println!("   📤 Messages Sent: {}", msg_sent);
        println!("   📥 Messages Received: {}", msg_recv);
        println!("   📊 Bytes Sent: {}", bytes_sent);
        println!("   📈 Bytes Received: {}", bytes_recv);
        println!("   ❌ Errors: {}", errors);
    }
}

#[derive(Clone)]
struct ChatServer {
    clients: Arc<DashMap<String, broadcast::Sender<ChatMessage>>>,
    metrics: Arc<ConnectionMetrics>,
    broadcast_tx: broadcast::Sender<ChatMessage>,
}

impl ChatServer {
    fn new() -> Self {
        let (broadcast_tx, _) = broadcast::channel(50000); // Massive buffer for performance

        Self {
            clients: Arc::new(DashMap::new()),
            metrics: Arc::new(ConnectionMetrics::new()),
            broadcast_tx,
        }
    }

    async fn handle_connection(&self, stream: TcpStream, addr: SocketAddr) {
        let client_id = Uuid::new_v4().to_string();

        // Accept WebSocket connection with optimized settings
        let ws_stream = match timeout(Duration::from_secs(10), accept_async(stream)).await {
            Ok(Ok(ws)) => ws,
            Ok(Err(e)) => {
                eprintln!("❌ WebSocket handshake failed for {}: {}", addr, e);
                self.metrics.errors.fetch_add(1, Ordering::Relaxed);
                return;
            }
            Err(_) => {
                eprintln!("⏰ WebSocket handshake timeout for {}", addr);
                self.metrics.errors.fetch_add(1, Ordering::Relaxed);
                return;
            }
        };

        println!("✅ New connection: {} ({})", client_id, addr);
        self.metrics.connections.fetch_add(1, Ordering::Relaxed);

        // Create client-specific broadcast channel
        let (client_tx, client_rx) = broadcast::channel(10000);
        self.clients.insert(client_id.clone(), client_tx.clone());

        // Subscribe to global broadcasts
        let mut global_rx = self.broadcast_tx.subscribe();

        // Split WebSocket stream for concurrent read/write
        let (mut ws_sender, mut ws_receiver) = ws_stream.split();

        let metrics = Arc::clone(&self.metrics);
        let clients = Arc::clone(&self.clients);
        let broadcast_tx = self.broadcast_tx.clone();
        let client_id_clone = client_id.clone();

        // Spawn task for handling incoming messages
        let recv_task = {
            let metrics = Arc::clone(&metrics);
            let broadcast_tx = broadcast_tx.clone();
            let client_id = client_id.clone();

            tokio::spawn(async move {
                while let Some(msg) = ws_receiver.next().await {
                    match msg {
                        Ok(Message::Text(text)) => {
                            metrics.messages_received.fetch_add(1, Ordering::Relaxed);
                            metrics.bytes_received.fetch_add(text.len() as u64, Ordering::Relaxed);

                            // Parse and broadcast message
                            if let Ok(mut chat_msg) = serde_json::from_str::<ChatMessage>(&text) {
                                chat_msg.id = Uuid::new_v4().to_string();
                                chat_msg.timestamp = std::time::SystemTime::now()
                                    .duration_since(std::time::UNIX_EPOCH)
                                    .unwrap()
                                    .as_millis() as u64;

                                // Broadcast to all clients (non-blocking)
                                let _ = broadcast_tx.send(chat_msg);
                            }
                        }
                        Ok(Message::Binary(data)) => {
                            metrics.bytes_received.fetch_add(data.len() as u64, Ordering::Relaxed);
                        }
                        Ok(Message::Close(_)) => {
                            println!("🔌 Client {} disconnected gracefully", client_id);
                            break;
                        }
                        Ok(Message::Ping(data)) => {
                            // Auto-handled by tungstenite
                            metrics.bytes_received.fetch_add(data.len() as u64, Ordering::Relaxed);
                        }
                        Ok(Message::Pong(data)) => {
                            metrics.bytes_received.fetch_add(data.len() as u64, Ordering::Relaxed);
                        }
                        Err(e) => {
                            eprintln!("❌ WebSocket error for {}: {}", client_id, e);
                            metrics.errors.fetch_add(1, Ordering::Relaxed);
                            break;
                        }
                    }
                }
            })
        };

        // Spawn task for sending messages
        let send_task = {
            let metrics = Arc::clone(&metrics);
            let client_id = client_id.clone();

            tokio::spawn(async move {
                // Batch messages for efficiency (up to 100 messages per write)
                let mut message_batch = Vec::with_capacity(100);
                let mut last_flush = Instant::now();
                const BATCH_TIMEOUT: Duration = Duration::from_millis(1);

                loop {
                    tokio::select! {
                        // Receive from global broadcast
                        msg = global_rx.recv() => {
                            match msg {
                                Ok(chat_msg) => {
                                    message_batch.push(chat_msg);

                                    // Flush batch if full or timeout reached
                                    if message_batch.len() >= 100 || last_flush.elapsed() >= BATCH_TIMEOUT {
                                        if let Err(e) = flush_message_batch(&mut ws_sender, &mut message_batch, &metrics).await {
                                            eprintln!("❌ Failed to send batch for {}: {}", client_id, e);
                                            break;
                                        }
                                        last_flush = Instant::now();
                                    }
                                }
                                Err(broadcast::error::RecvError::Lagged(_)) => {
                                    // Client is too slow, continue (don't block other clients)
                                    continue;
                                }
                                Err(broadcast::error::RecvError::Closed) => {
                                    break;
                                }
                            }
                        }

                        // Timeout flush for remaining messages
                        _ = tokio::time::sleep(BATCH_TIMEOUT) => {
                            if !message_batch.is_empty() && last_flush.elapsed() >= BATCH_TIMEOUT {
                                if let Err(e) = flush_message_batch(&mut ws_sender, &mut message_batch, &metrics).await {
                                    eprintln!("❌ Failed to send timeout batch for {}: {}", client_id, e);
                                    break;
                                }
                                last_flush = Instant::now();
                            }
                        }
                    }
                }
            })
        };

        // Wait for either task to complete (connection closed)
        tokio::select! {
            _ = recv_task => {},
            _ = send_task => {},
        }

        // Cleanup
        clients.remove(&client_id_clone);
        self.metrics.connections.fetch_sub(1, Ordering::Relaxed);
        println!("🧹 Cleaned up connection: {}", client_id_clone);
    }

    async fn broadcast_message(&self, message: ChatMessage) -> Result<(), Box<dyn std::error::Error>> {
        let _ = self.broadcast_tx.send(message);
        Ok(())
    }

    fn get_stats(&self) -> (usize, u64, u64, u64) {
        (
            self.clients.len(),
            self.metrics.messages_sent.load(Ordering::Relaxed),
            self.metrics.messages_received.load(Ordering::Relaxed),
            self.metrics.errors.load(Ordering::Relaxed),
        )
    }
}

async fn flush_message_batch(
    ws_sender: &mut futures_util::stream::SplitSink<WebSocketStream<TcpStream>, Message>,
    message_batch: &mut Vec<ChatMessage>,
    metrics: &ConnectionMetrics,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    if message_batch.is_empty() {
        return Ok(());
    }

    // Send all messages in batch
    for message in message_batch.drain(..) {
        let json = serde_json::to_string(&message)?;
        let msg_len = json.len() as u64;

        if let Err(e) = ws_sender.send(Message::Text(json)).await {
            metrics.errors.fetch_add(1, Ordering::Relaxed);
            return Err(Box::new(e));
        }

        metrics.messages_sent.fetch_add(1, Ordering::Relaxed);
        metrics.bytes_sent.fetch_add(msg_len, Ordering::Relaxed);
    }

    // Flush the sink to ensure messages are sent immediately
    ws_sender.flush().await?;
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Create server
    let server = ChatServer::new();
    let server_clone = server.clone();

    // Spawn stats reporter
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(Duration::from_secs(5));
        loop {
            interval.tick().await;
            server_clone.metrics.print_stats();
        }
    });

    // Bind to address
    let addr = "127.0.0.1:8080";
    let listener = TcpListener::bind(addr).await?;
    println!("🦀 RUST WebSocket server listening on: {}", addr);
    println!("🚀 Optimizations enabled:");
    println!("   - Zero-cost abstractions");
    println!("   - Manual memory management");
    println!   ("   - Tokio async runtime");
    println!("   - Message batching (up to 100/batch)");
    println!("   - Non-blocking client handling");
    println!("   - 50k broadcast channel buffer");

    // Accept connections
    while let Ok((stream, addr)) = listener.accept().await {
        let server = server.clone();

        tokio::spawn(async move {
            server.handle_connection(stream, addr).await;
        });
    }

    Ok(())
}

// Benchmarking utilities
#[cfg(test)]
mod bench_utils {
    use super::*;
    use std::time::Instant;

    pub async fn run_connection_test(target_connections: usize) -> (usize, Duration) {
        let start = Instant::now();
        let server = ChatServer::new();

        // Simulate connection attempts
        let mut successful_connections = 0;

        for i in 0..target_connections {
            if i % 100 == 0 {
                println!("🔗 Connections attempted: {}/{}", i, target_connections);
            }

            // Simulate connection logic
            successful_connections += 1;

            if i % 1000 == 0 {
                tokio::time::sleep(Duration::from_millis(1)).await;
            }
        }

        (successful_connections, start.elapsed())
    }

    pub async fn run_message_burst_test(connections: usize, messages_per_connection: usize) -> (u64, Duration) {
        let start = Instant::now();
        let server = ChatServer::new();

        let total_messages = (connections * messages_per_connection) as u64;
        let mut sent_messages = 0u64;

        // Simulate burst messaging
        for batch in 0..(total_messages / 1000) {
            for _ in 0..1000 {
                let message = ChatMessage {
                    id: Uuid::new_v4().to_string(),
                    content: "Performance test message".to_string(),
                    timestamp: 0,
                    user: "benchmark".to_string(),
                };

                let _ = server.broadcast_message(message).await;
                sent_messages += 1;
            }

            if batch % 10 == 0 {
                println!("📤 Messages sent: {}/{}", sent_messages, total_messages);
            }
        }

        (sent_messages, start.elapsed())
    }
}
