import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { sendChatMessage, sendChatMessageStream } from "../axios/chatService";
import IntroText from "./IntroText";
import { v4 as uuidv4 } from "uuid"; // for generating unique session ids

interface Message {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // generate a session id for this browser session
  const [sessionId] = useState<string>(() => uuidv4());

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    const userInput = input;
    setInput("");
    setLoading(true);

    // Add empty assistant message for streaming
    const assistantMessageIndex = messages.length + 1;
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", isStreaming: true }
    ]);

    try {
      let fullResponse = "";
      
      await sendChatMessageStream(
        sessionId,
        userInput,
        // onChunk - this fires for each word/chunk
        (chunk: string) => {
          fullResponse += chunk;
          setMessages((prev) => {
            const newMessages = [...prev];
            if (newMessages[assistantMessageIndex]) {
              newMessages[assistantMessageIndex] = {
                ...newMessages[assistantMessageIndex],
                content: fullResponse,
                isStreaming: true
              };
            }
            return newMessages;
          });
        },
        // onComplete
        () => {
          setMessages((prev) => {
            const newMessages = [...prev];
            if (newMessages[assistantMessageIndex]) {
              newMessages[assistantMessageIndex] = {
                ...newMessages[assistantMessageIndex],
                isStreaming: false
              };
            }
            return newMessages;
          });
          setLoading(false);
        },
        // onError - fallback to non-streaming
        async (error) => {
          console.error("Streaming failed:", error);
          try {
            const answer = await sendChatMessage(sessionId, userInput);
            setMessages((prev) => {
              const newMessages = [...prev];
              if (newMessages[assistantMessageIndex]) {
                newMessages[assistantMessageIndex] = {
                  role: "assistant",
                  content: answer,
                  isStreaming: false
                };
              }
              return newMessages;
            });
          } catch (fallbackError) {
            setMessages((prev) => {
              const newMessages = [...prev];
              if (newMessages[assistantMessageIndex]) {
                newMessages[assistantMessageIndex] = {
                  role: "assistant",
                  content: "I'm sorry, I'm having technical difficulties. Please try again.",
                  isStreaming: false
                };
              }
              return newMessages;
            });
          }
          setLoading(false);
        }
      );
    } catch (err) {
      console.error("Error:", err);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4 pb-8 flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto space-y-4 scrollbar-hide p-4 rounded">
        {messages.length === 0 && !loading ? (
          <IntroText />
        ) : (
          <>
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex w-full ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`p-2 rounded-lg max-w-lg relative ${
                    m.role === "user"
                      ? "bg-green-200 text-black"
                      : "bg-gray-200 text-black"
                  }`}
                >
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                  {/* Show typing indicator ONLY when streaming but no content yet */}
                  {m.isStreaming && m.content.trim() === "" && (
                    <div className="flex items-center mt-1">
                      <div className="flex gap-1">
                        <span className="animate-bounce text-xs">.</span>
                        <span className="animate-bounce text-xs [animation-delay:0.2s]">.</span>
                        <span className="animate-bounce text-xs [animation-delay:0.4s]">.</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input and send button in one rounded container */}
      <div className="flex items-center border rounded-full p-1 px-2 mt-2 bg-white">
        <input
          className="flex-1 p-3 rounded-full outline-none border-none"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
          disabled={loading}
        />
        <button
          className={`p-2 rounded-full transition flex items-center justify-center ${
            loading 
              ? "bg-gray-400 cursor-not-allowed" 
              : "bg-green-500 hover:bg-green-700 text-white"
          }`}
          onClick={handleSendMessage}
          disabled={loading}
        >
          {loading ? (
            <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}