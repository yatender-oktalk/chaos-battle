package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net"
    "net/http"
    "runtime"
    "sync"
    "sync/atomic"
    "time"

    "github.com/gorilla/websocket"
)

// Ultra-optimized for maximum performance
var (
    connectionCount int64
    messageCount    int64
)

type Hub struct {
    clients    sync.Map // Use sync.Map for better concurrent performance
    broadcast  chan []byte
    register   chan *Client
    unregister chan *Client
}

type Client struct {
    hub    *Hub
    conn   *websocket.Conn
    send   chan []byte
    id     string
    closed int32 // atomic flag
}

type Message struct {
    Type    string    `json:"type"`
    User    string    `json:"user"`
    Content string    `json:"content"`
    Time    time.Time `json:"time"`
}

// Ultra-optimized upgrader
var upgrader = websocket.Upgrader{
    ReadBufferSize:    2048,  // Larger buffers
    WriteBufferSize:   2048,
    HandshakeTimeout:  5 * time.Second,
    EnableCompression: false, // Disable compression for max speed
    CheckOrigin: func(r *http.Request) bool {
        return true
    },
}

func newHub() *Hub {
    return &Hub{
        broadcast:  make(chan []byte, 10000), // Massive buffer
        register:   make(chan *Client, 1000),
        unregister: make(chan *Client, 1000),
    }
}

func (h *Hub) run() {
    for {
        select {
        case client := <-h.register:
            h.clients.Store(client, true)
            count := atomic.AddInt64(&connectionCount, 1)
            if count%500 == 0 {
                log.Printf("✅ %d connections established", count)
            }

        case client := <-h.unregister:
            if _, ok := h.clients.LoadAndDelete(client); ok {
                atomic.AddInt64(&connectionCount, -1)
                if atomic.CompareAndSwapInt32(&client.closed, 0, 1) {
                    close(client.send)
                }
            }

        case message := <-h.broadcast:
            atomic.AddInt64(&messageCount, 1)

            // Ultra-fast broadcast using sync.Map
            h.clients.Range(func(key, value interface{}) bool {
                client := key.(*Client)
                select {
                case client.send <- message:
                default:
                    // Non-blocking: if client is slow, disconnect it
                    h.clients.Delete(client)
                    if atomic.CompareAndSwapInt32(&client.closed, 0, 1) {
                        close(client.send)
                    }
                }
                return true
            })
        }
    }
}

func serveWS(hub *Hub, w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        return // Silent failure for performance
    }

    clientID := r.URL.Query().Get("id")
    if clientID == "" {
        clientID = fmt.Sprintf("u%d", time.Now().UnixNano()%1000000)
    }

    client := &Client{
        hub:  hub,
        conn: conn,
        send: make(chan []byte, 1024), // Larger send buffer
        id:   clientID,
    }

    client.hub.register <- client

    // Start goroutines
    go client.writePump()
    go client.readPump()
}

func (c *Client) readPump() {
    defer func() {
        c.hub.unregister <- c
        c.conn.Close()
    }()

    // Optimized settings for maximum throughput
    c.conn.SetReadLimit(2048)
    c.conn.SetReadDeadline(time.Now().Add(120 * time.Second))
    c.conn.SetPongHandler(func(string) error {
        c.conn.SetReadDeadline(time.Now().Add(120 * time.Second))
        return nil
    })

    for {
        _, message, err := c.conn.ReadMessage()
        if err != nil {
            break
        }

        // Fast path: minimal processing
        var msg Message
        if json.Unmarshal(message, &msg) == nil {
            msg.User = c.id
            msg.Time = time.Now()

            if data, err := json.Marshal(msg); err == nil {
                select {
                case c.hub.broadcast <- data:
                default:
                    // Drop message if broadcast is full (non-blocking)
                }
            }
        }
    }
}

func (c *Client) writePump() {
    ticker := time.NewTicker(60 * time.Second)
    defer func() {
        ticker.Stop()
        c.conn.Close()
    }()

    for {
        select {
        case message, ok := <-c.send:
            if !ok {
                c.conn.WriteMessage(websocket.CloseMessage, []byte{})
                return
            }

            c.conn.SetWriteDeadline(time.Now().Add(5 * time.Second))

            // Ultra-fast write with batching
            w, err := c.conn.NextWriter(websocket.TextMessage)
            if err != nil {
                return
            }

            w.Write(message)

            // Batch additional messages
            n := len(c.send)
            for i := 0; i < n && i < 100; i++ { // Limit batching
                select {
                case msg := <-c.send:
                    w.Write([]byte{'\n'})
                    w.Write(msg)
                default:
                    break
                }
            }

            if err := w.Close(); err != nil {
                return
            }

        case <-ticker.C:
            c.conn.SetWriteDeadline(time.Now().Add(5 * time.Second))
            if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
                return
            }
        }
    }
}

func main() {
    // Ultra-optimize Go runtime
    runtime.GOMAXPROCS(runtime.NumCPU())
    runtime.GC() // Clean start

    log.Println("🔥 ULTRA-OPTIMIZED Go Chat Server")
    log.Printf("🖥️  CPU cores: %d", runtime.NumCPU())

    hub := newHub()
    go hub.run()

    // Stats goroutine
    go func() {
        for {
            time.Sleep(5 * time.Second)
            conn := atomic.LoadInt64(&connectionCount)
            msg := atomic.LoadInt64(&messageCount)
            log.Printf("📊 Stats: %d connections, %d messages, %d goroutines",
                conn, msg, runtime.NumGoroutine())
        }
    }()

    // Ultra-optimized HTTP server
    server := &http.Server{
        Addr:           ":8080",
        ReadTimeout:    10 * time.Second,
        WriteTimeout:   10 * time.Second,
        IdleTimeout:    30 * time.Second,
        MaxHeaderBytes: 4096,
    }

    // Custom listener with optimizations
    listener, err := net.Listen("tcp", ":8080")
    if err != nil {
        log.Fatal(err)
    }

    // If available, optimize the listener
    if tcpListener, ok := listener.(*net.TCPListener); ok {
        listener = &optimizedListener{tcpListener}
    }

    // Routes
    http.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
        serveWS(hub, w, r)
    })

    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]interface{}{
            "status":      "healthy",
            "connections": atomic.LoadInt64(&connectionCount),
            "messages":    atomic.LoadInt64(&messageCount),
            "goroutines":  runtime.NumGoroutine(),
        })
    })

    http.HandleFunc("/stats", func(w http.ResponseWriter, r *http.Request) {
        var m runtime.MemStats
        runtime.ReadMemStats(&m)

        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]interface{}{
            "connections":    atomic.LoadInt64(&connectionCount),
            "messages":       atomic.LoadInt64(&messageCount),
            "goroutines":     runtime.NumGoroutine(),
            "memory_mb":      m.Alloc / 1024 / 1024,
            "gc_cycles":      m.NumGC,
        })
    })

    log.Println("🎯 Server ready for ULTRA PERFORMANCE testing on :8080")
    log.Fatal(server.Serve(listener))
}

// Optimized listener wrapper
type optimizedListener struct {
    *net.TCPListener
}

func (ln *optimizedListener) Accept() (net.Conn, error) {
    conn, err := ln.TCPListener.AcceptTCP()
    if err != nil {
        return nil, err
    }

    // Optimize TCP connection
    conn.SetKeepAlive(true)
    conn.SetKeepAlivePeriod(30 * time.Second)
    conn.SetNoDelay(true) // Disable Nagle's algorithm

    return conn, nil
}
