"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, StopCircle, PanelLeft, Plus, Mic, Copy, RotateCcw, Check } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Sidebar from "./Sidebar";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [hoveredButton, setHoveredButton] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [sessionId, setSessionId] = useState("");

  useEffect(() => {
    setSessionId(crypto.randomUUID());
  }, []);

  const startNewChat = () => {
    setSessionId(crypto.randomUUID());
    setMessages([]);
    setInput("");
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  };

  const handleCopy = (content: string, index: number) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleRegenerate = async () => {
    const lastUserMessage = messages.slice().reverse().find(msg => msg.role === 'user');
    if (lastUserMessage && !isLoading) {
      setMessages(prev => prev.slice(0, -1));
      await handleSubmit(undefined, lastUserMessage.content);
    }
  };

  const handleSubmit = async (e?: React.FormEvent, regenerateMessage?: string) => {
    e?.preventDefault();
    const messageContent = regenerateMessage || input;
    if (!messageContent.trim() || isLoading) return;

    if (!regenerateMessage) {
      setInput("");
      if (textareaRef.current) textareaRef.current.style.height = "auto";
      setMessages((prev) => [...prev, { role: "user", content: messageContent }]);
    }

    setIsLoading(true);
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch("http://localhost:8000/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symptoms: messageContent,
          history: "None provided",
          session_id: sessionId,
          user_id: "web_user"
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        assistantMessage += chunk;

        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          lastMessage.content = assistantMessage;
          return newMessages;
        });
      }
    } catch (error: any) {
      if (error.name === "AbortError") {
        console.log("Generation stopped by user");
      } else {
        console.error("Error:", error);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Sorry, I encountered an error." },
        ]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const Tooltip = ({ text, show }: { text: string; show: boolean }) => (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          transition={{ duration: 0.15 }}
          className="absolute top-full mt-2 px-2 py-1 bg-[#565869] text-white text-xs rounded whitespace-nowrap z-50 pointer-events-none"
        >
          {text}
        </motion.div>
      )}
    </AnimatePresence>
  );

  return (
    <div className="flex h-screen bg-[#202123] text-[#ececf1] overflow-hidden">
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.div
            initial={{ x: -260, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -260, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="z-40"
          >
            <Sidebar
              isOpen={isSidebarOpen}
              toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
              onNewChat={startNewChat}
            />    </motion.div>
        )}
      </AnimatePresence>

      <div className="flex-1 flex flex-col h-full min-w-0">
        {/* Top Navigation Bar - Higher z-index to stay above sidebar */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-[#3c3d3f] bg-[#202123] relative z-50">
          <div className="flex items-center gap-3">
            <div
              className="relative"
              onMouseEnter={() => setHoveredButton('sidebar')}
              onMouseLeave={() => setHoveredButton(null)}
            >
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="p-2 hover:bg-[#343541] rounded-lg text-[#8e8e90] hover:text-[#ececf1] transition-colors"
              >
                <PanelLeft className="w-5 h-5" />
              </button>
              <Tooltip text={isSidebarOpen ? "Close sidebar" : "Open sidebar"} show={hoveredButton === 'sidebar'} />
            </div>
            <span className="font-semibold text-[#ececf1] font-[family-name:var(--font-inter)]">MediGraph 1.0</span>
          </div>
          <div
            className="relative"
            onMouseEnter={() => setHoveredButton('menu')}
            onMouseLeave={() => setHoveredButton(null)}
          >
            <button className="p-2 hover:bg-[#343541] rounded-lg text-[#8e8e90] hover:text-[#ececf1] transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 16 16">
                <circle cx="8" cy="2" r="1.5" /><circle cx="8" cy="8" r="1.5" /><circle cx="8" cy="14" r="1.5" />
              </svg>
            </button>
            <Tooltip text="More options" show={hoveredButton === 'menu'} />
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="h-full flex flex-col items-center justify-center px-4 pb-32"
            >
              <h1 className="text-4xl font-semibold text-[#ececf1] font-[family-name:var(--font-inter)] mb-12">How can I help you, Jk?</h1>
            </motion.div>
          ) : (
            <div className="w-full px-4 pb-32 pt-6">
              <AnimatePresence>
                {messages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="mb-6"
                  >
                    {msg.role === "user" ? (
                      /* User Message - Right-aligned bubble */
                      <div className="flex justify-end max-w-5xl mx-auto">
                        <div className="max-w-[75%] bg-[#343541] rounded-2xl px-4 py-3">
                          <div className="text-[15px] text-[#ececf1] leading-relaxed whitespace-pre-wrap break-words">
                            {msg.content}
                          </div>
                        </div>
                      </div>
                    ) : (
                      /* AI Message - Full width with left avatar */
                      <div className="flex gap-3 items-start max-w-5xl mx-auto">
                        <div className="flex-shrink-0 mt-1">
                          <div className="w-8 h-8 rounded-full bg-[#19c37d] flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-[15px] text-[#ececf1] leading-relaxed prose prose-invert max-w-none">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {msg.content}
                            </ReactMarkdown>
                            {isLoading && idx === messages.length - 1 && (
                              <motion.span
                                animate={{ opacity: [0.4, 1, 0.4] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                                className="inline-block w-1.5 h-4 ml-1 bg-gray-400 align-middle"
                              />
                            )}
                          </div>

                          {/* Action Buttons */}
                          {!isLoading && (
                            <motion.div
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              transition={{ delay: 0.3 }}
                              className="flex items-center gap-2 mt-3"
                            >
                              <div
                                className="relative"
                                onMouseEnter={() => setHoveredButton(`copy-${idx}`)}
                                onMouseLeave={() => setHoveredButton(null)}
                              >
                                <button
                                  onClick={() => handleCopy(msg.content, idx)}
                                  className="p-2 hover:bg-[#343541] rounded-lg text-[#8e8e90] hover:text-[#ececf1] transition-colors"
                                >
                                  {copiedIndex === idx ? (
                                    <Check className="w-4 h-4 text-green-500" />
                                  ) : (
                                    <Copy className="w-4 h-4" />
                                  )}
                                </button>
                                <Tooltip text={copiedIndex === idx ? "Copied!" : "Copy"} show={hoveredButton === `copy-${idx}`} />
                              </div>

                              {idx === messages.length - 1 && (
                                <div
                                  className="relative"
                                  onMouseEnter={() => setHoveredButton('regenerate')}
                                  onMouseLeave={() => setHoveredButton(null)}
                                >
                                  <button
                                    onClick={handleRegenerate}
                                    className="p-2 hover:bg-[#343541] rounded-lg text-[#8e8e90] hover:text-[#ececf1] transition-colors"
                                  >
                                    <RotateCcw className="w-4 h-4" />
                                  </button>
                                  <Tooltip text="Regenerate" show={hoveredButton === 'regenerate'} />
                                </div>
                              )}
                            </motion.div>
                          )}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Input Area - Fixed at Bottom */}
          <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-[#202123] via-[#202123] to-transparent pb-6 pt-4">
            <div className="max-w-3xl mx-auto px-4">
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="relative flex items-center w-full px-4 py-3 bg-[#40414f] rounded-xl border border-[#565869] shadow-sm"
              >
                <div
                  className="relative"
                  onMouseEnter={() => setHoveredButton('attach')}
                  onMouseLeave={() => setHoveredButton(null)}
                >
                  <button className="p-1 text-[#8e8e90] hover:text-[#ececf1] transition-colors mr-2">
                    <Plus className="w-5 h-5" />
                  </button>
                  <Tooltip text="Attach file" show={hoveredButton === 'attach'} />
                </div>

                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask anything"
                  className="flex-1 max-h-[200px] bg-transparent border-0 focus:outline-none resize-none text-[#ececf1] placeholder-[#8e8e90] text-[15px] leading-relaxed font-[family-name:var(--font-lato)]"
                  rows={1}
                />

                <div
                  className="relative"
                  onMouseEnter={() => setHoveredButton('voice')}
                  onMouseLeave={() => setHoveredButton(null)}
                >
                  <button className="p-1 text-[#8e8e90] hover:text-[#ececf1] transition-colors mx-2">
                    <Mic className="w-5 h-5" />
                  </button>
                  <Tooltip text="Voice input" show={hoveredButton === 'voice'} />
                </div>

                {isLoading ? (
                  <div
                    className="relative"
                    onMouseEnter={() => setHoveredButton('stop')}
                    onMouseLeave={() => setHoveredButton(null)}
                  >
                    <button
                      onClick={stopGeneration}
                      className="p-2 bg-white text-black rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      <StopCircle className="w-4 h-4 fill-current" />
                    </button>
                    <Tooltip text="Stop generating" show={hoveredButton === 'stop'} />
                  </div>
                ) : (
                  <div
                    className="relative"
                    onMouseEnter={() => setHoveredButton('send')}
                    onMouseLeave={() => setHoveredButton(null)}
                  >
                    <button
                      onClick={() => handleSubmit()}
                      disabled={!input.trim()}
                      className="p-2 text-[#8e8e90] hover:text-[#ececf1] transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                    <Tooltip text="Send message" show={hoveredButton === 'send' && !!input.trim()} />
                  </div>
                )}
              </motion.div>

              <p className="text-center text-xs text-[#8e8e90] mt-3">
                MediGraph can make mistakes. Consult a doctor for medical advice.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
