import { useState, useEffect, useRef } from "react";
import "./ChatPage.css";

const API_BASE_URL = "http://localhost:8000";
const CHATS_STORAGE_KEY = "rag_chat_history";

export default function ChatPage() {
  // State
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chats, setChats] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeChatId, setActiveChatId] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Persistence and Auto-scroll Effects
  useEffect(() => {
    const savedChats = localStorage.getItem(CHATS_STORAGE_KEY);
    if (savedChats) {
      try {
        setChats(JSON.parse(savedChats));
      } catch (e) {
        console.error("Failed to parse saved chats:", e);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Helper Functions
  const generateId = () =>
    Date.now().toString(36) + Math.random().toString(36).substr(2);
  const formatTimestamp = (timestamp) =>
    new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

  const handleNewChat = () => {
    setMessages([]);
    setActiveChatId(null);
    setSidebarOpen(false);
    inputRef.current?.focus();
  };

  const handleSelectChat = (chatId) => {
    const chat = chats.find((c) => c.id === chatId);
    if (chat) {
      setMessages(chat.messages);
      setActiveChatId(chatId);
      setSidebarOpen(false);
    }
  };

  const handleDeleteChat = (e, chatId) => {
    e.stopPropagation();
    const newChats = chats.filter((c) => c.id !== chatId);
    setChats(newChats);
    if (activeChatId === chatId) handleNewChat();
  };

  const saveCurrentChat = (updatedMessages) => {
    if (updatedMessages.length === 0) return;
    const firstUserMessage = updatedMessages.find((m) => m.role === "user");
    const title = firstUserMessage
      ? firstUserMessage.content.slice(0, 30) +
        (firstUserMessage.content.length > 30 ? "..." : "")
      : "New Chat";

    if (activeChatId) {
      setChats(
        chats.map((c) =>
          c.id === activeChatId
            ? { ...c, messages: updatedMessages, title }
            : c,
        ),
      );
    } else {
      const newChat = {
        id: generateId(),
        title,
        messages: updatedMessages,
        timestamp: Date.now(),
      };
      setChats([newChat, ...chats]);
      setActiveChatId(newChat.id);
    }
  };

  const handleSendMessage = async () => {
    const userMessage = inputValue.trim();
    if (!userMessage || isLoading) return;

    const userMsg = {
      id: generateId(),
      role: "user",
      content: userMessage,
      timestamp: Date.now(),
    };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage }),
      });

      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let aiResponse = "";
      let aiMessageId = generateId();

      setMessages((prev) => [
        ...prev,
        { id: aiMessageId, role: "ai", content: "", timestamp: Date.now() },
      ]);

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          aiResponse += decoder.decode(value, { stream: true });
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessageId ? { ...msg, content: aiResponse } : msg,
            ),
          );
        }
      }
      saveCurrentChat([
        ...newMessages,
        {
          id: aiMessageId,
          role: "ai",
          content: aiResponse,
          timestamp: Date.now(),
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: "ai",
          content: "Error processing request.",
          timestamp: Date.now(),
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-page">
      <div
        className={`sidebar-overlay ${sidebarOpen ? "visible" : ""}`}
        onClick={() => setSidebarOpen(false)}
      ></div>

      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <h2>Support AI</h2>
          <button className="new-chat-btn" onClick={handleNewChat}>
            <i className="fa-solid fa-plus" style={{ marginRight: "8px" }}></i>
            New Chat
          </button>
        </div>

        <div className="chat-history">
          <div className="chat-history-title">Recent Chats</div>
          {chats.length === 0 ? (
            <div className="empty-chats">No conversations yet.</div>
          ) : (
            chats.map((chat) => (
              <div
                key={chat.id}
                className={`chat-item ${activeChatId === chat.id ? "active" : ""}`}
                onClick={() => handleSelectChat(chat.id)}
              >
                <span className="chat-item-title">{chat.title}</span>
                <button
                  className="chat-item-delete"
                  onClick={(e) => handleDeleteChat(e, chat.id)}
                >
                  <i className="fa-solid fa-trash-can"></i>
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      <main className="chat-main">
        <header className="chat-header">
          <div className="chat-header-title">
            <button
              className="menu-toggle"
              onClick={() => setSidebarOpen(true)}
            >
              <i className="fa-solid fa-bars"></i>
            </button>
            <h2>Chat</h2>
          </div>
        </header>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <div className="welcome-icon">
                <i
                  className="fa-solid fa-robot"
                  style={{ fontSize: "40px" }}
                ></i>
              </div>
              <h3>Welcome to Support AI</h3>
              <p>Ask me anything about tickets or documentation.</p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`message ${message.role}`}>
                <div className="message-bubble">{message.content}</div>
                <div className="message-timestamp">
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message ai">
              <div className="typing-indicator">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef}></div>
        </div>

        <div className="input-area">
          <div className="input-container">
            <textarea
              ref={inputRef}
              className="message-input"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              rows={1}
              disabled={isLoading}
            />
            <button
              className="send-btn"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
            >
              <i className="fa-solid fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
