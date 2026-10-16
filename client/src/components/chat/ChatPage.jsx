import { useEffect, useRef, useState } from "react";
import "./ChatPage.css";

const API_BASE_URL = (import.meta.env.VITE_API_URL ?? "").replace(/\/+$/, "");

const suggestedQuestions = [
  "How do I track my order?",
  "How do I return an item?",
  "How do I update my account details?",
];

const renderMessageContent = (content, role) => {
  if (role !== "ai") return content;

  return content
    .replace(/[ \t]+(?=\d+\.\s)/g, "\n")
    .split("\n")
    .map((line, lineIndex) => (
      <span key={lineIndex}>
        {lineIndex > 0 && <br />}
        {line.split(/(\*\*[^*]+\*\*)/g).map((part, partIndex) =>
          part.startsWith("**") && part.endsWith("**") ? (
            <strong key={partIndex}>{part.slice(2, -2)}</strong>
          ) : (
            part
          ),
        )}
      </span>
    ));
};

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const requestControllerRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
    return () => requestControllerRef.current?.abort();
  }, []);

  const handleNewConversation = () => {
    requestControllerRef.current?.abort();
    requestControllerRef.current = null;
    setIsLoading(false);
    setMessages([]);
    setInputValue("");
    inputRef.current?.focus();
  };

  const handleSendMessage = async (question = inputValue) => {
    const userMessage = question.trim();
    if (!userMessage || isLoading) return;

    const controller = new AbortController();
    requestControllerRef.current = controller;
    const userMsg = {
      id: crypto.randomUUID(),
      role: "user",
      content: userMessage,
    };
    const aiMessageId = crypto.randomUUID();

    setMessages((currentMessages) => [...currentMessages, userMsg]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage }),
        signal: controller.signal,
      });

      if (!response.ok) {
        let detail = `Request failed (${response.status}).`;
        try {
          const errorBody = await response.json();
          if (typeof errorBody.detail === "string") detail = errorBody.detail;
        } catch {
          // Keep the HTTP status as the diagnostic when the response is not JSON.
        }
        throw new Error(detail);
      }
      if (!response.body) {
        throw new Error("The chat response stream is unavailable.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiResponse = "";
      const appendAssistantText = (text) => {
        if (!text) return;
        aiResponse += text;
        setMessages((currentMessages) => {
          const hasAssistantMessage = currentMessages.some(
            (message) => message.id === aiMessageId,
          );
          if (!hasAssistantMessage) {
            return [
              ...currentMessages,
              { id: aiMessageId, role: "ai", content: aiResponse },
            ];
          }
          return currentMessages.map((message) =>
            message.id === aiMessageId
              ? { ...message, content: aiResponse }
              : message,
          );
        });
      };

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (controller.signal.aborted) return;
          if (done) break;

          appendAssistantText(decoder.decode(value, { stream: true }));
        }

        appendAssistantText(decoder.decode());
      } finally {
        reader.releaseLock();
      }

      if (!aiResponse.trim()) {
        throw new Error("The assistant returned an empty response.");
      }

    } catch (error) {
      if (controller.signal.aborted || error?.name === "AbortError") return;
      console.error("Chat request failed:", error);
      setMessages((currentMessages) => {
        const messagesWithoutEmptyResponse = currentMessages.filter(
          (message) =>
            message.id !== aiMessageId || message.content.trim() !== "",
        );
        return [
          ...messagesWithoutEmptyResponse,
          {
            id: crypto.randomUUID(),
            role: "ai",
            content: `${error.message || "The support service is unavailable."} Please try again.`,
            isError: true,
          },
        ];
      });
    } finally {
      if (requestControllerRef.current === controller) {
        requestControllerRef.current = null;
        setIsLoading(false);
      }
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <main className="support-chat">
      <header className="support-header">
        <a className="support-brand" href="/" aria-label="Support home">
          <span className="support-brand-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" fill="none">
              <path
                d="M8 16.5 13.2 22 24 10"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <span className="support-brand-name">Customer care</span>
        </a>

        {messages.length > 0 && (
          <button
            className="conversation-reset"
            type="button"
            onClick={handleNewConversation}
          >
            Start over
          </button>
        )}
      </header>

      <section className="conversation-panel" aria-label="Support conversation">
        {messages.length === 0 ? (
          <div className="conversation-welcome">
            <span className="welcome-eyebrow">HERE TO HELP</span>
            <h1>What can we help<br className="welcome-break" /> you with?</h1>
            <p>
              Ask us about an order, a return, or your account. We’ll help you
              find the next step.
            </p>

            <div className="suggested-questions" aria-label="Common questions">
              {suggestedQuestions.map((question) => (
                <button
                  className="suggestion-button"
                  key={question}
                  type="button"
                  onClick={() => {
                    setInputValue(question);
                    inputRef.current?.focus();
                  }}
                >
                  <span>{question}</span>
                  <span className="suggestion-arrow" aria-hidden="true">
                    &rarr;
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="conversation-messages" aria-live="polite">
            {messages.map((message) => (
              <article
                className={`conversation-message ${message.role}${message.isError ? " message-error" : ""}`}
                key={message.id}
              >
                {message.role === "ai" && (
                  <div className="message-author">
                    <span className="message-author-mark" aria-hidden="true">
                      C
                    </span>
                    <span>Customer care</span>
                  </div>
                )}
                <div
                  className="message-content"
                  role={message.isError ? "alert" : undefined}
                >
                  {renderMessageContent(message.content, message.role)}
                </div>
              </article>
            ))}

            {isLoading && (
              <div className="response-loading" role="status">
                <span className="loading-indicator" aria-hidden="true" />
                Finding an answer
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        <form
          className="composer"
          onSubmit={(event) => {
            event.preventDefault();
            handleSendMessage();
          }}
        >
          <label className="visually-hidden" htmlFor="support-question">
            Your message
          </label>
          <textarea
            id="support-question"
            ref={inputRef}
            className="message-input"
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Write your message..."
            rows={1}
            maxLength={1500}
            disabled={isLoading}
          />
          <div className="composer-footer">
            <span className="composer-hint">Press Enter to send</span>
            <button
              className="send-button"
              type="submit"
              aria-label="Send message"
              disabled={!inputValue.trim() || isLoading}
            >
              <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path
                  d="M3.5 10h12m-5-5 5 5-5 5"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        </form>

        <p className="conversation-note">
          Replies are based on the information available in our help center.
        </p>
      </section>
    </main>
  );
}
