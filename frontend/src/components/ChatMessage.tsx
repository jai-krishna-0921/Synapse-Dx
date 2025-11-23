"use client";

import { Bot, User, ThumbsUp, ThumbsDown, Copy } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AnimatePresence, motion } from "framer-motion";
import TriageCard from "./TriageCard";
import { Tooltip } from "react-tooltip";

interface Message {
  role: "user" | "assistant";
  content: string;
  data?: any;
}

interface ChatMessageProps {
  message: Message;
  isLoading: boolean;
  isLastMessage: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isLoading, isLastMessage }) => {
  const { role, content, data } = message;
  const isUser = role === "user";

  const renderContent = () => {
    if (data && data.triageLevel) {
      return (
        <TriageCard
          diagnosis={data.diagnosis}
          triageLevel={data.triageLevel}
          reasoning={data.reasoning}
          graphContext={data.graphContext}
          vectorContext={data.vectorContext}
        />
      );
    }

    const components = {
      code({ node, inline, className, children, ...props }: any) {
        const match = /language-(\w+)/.exec(className || "");
        return !inline && match ? (
          <div className="relative">
            <SyntaxHighlighter
              style={oneDark}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
            <button data-tooltip-id="copy-tooltip" data-tooltip-content="Copy code" className="absolute top-2 right-2 p-1.5 bg-gray-700 rounded-lg text-gray-300 hover:bg-gray-600">
              <Copy className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <code className={className} {...props}>
            {children}
          </code>
        );
      },
    };

    return (
      <div className="prose prose-invert max-w-none prose-p:leading-relaxed">
        <Markdown components={components} remarkPlugins={[remarkGfm]}>
          {content}
        </Markdown>
        {isLoading && isLastMessage && (
          <span className="inline-block w-2 h-4 ml-1 bg-gray-400 animate-pulse align-middle rounded-sm" />
        )}
      </div>
    );
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2 }}
        className="group w-full text-gray-100 border-b border-black/10 dark:border-gray-900/50"
      >
        <div className="flex gap-4 md:gap-6 m-auto py-6">
          <div className="flex-shrink-0 flex flex-col relative items-end">
            {isUser ? (
              <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-sm font-medium text-white">
                JK
              </div>
            ) : (
              <div className="w-8 h-8 rounded-full bg-[#19c37d] flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
          </div>

          <div className="relative flex-1 overflow-hidden">
            <div className="font-semibold text-sm mb-2 opacity-90">
              {isUser ? "You" : "MediGraph"}
            </div>
            {renderContent()}
          </div>
          {!isUser && (
            <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2">
              <button data-tooltip-id="like-tooltip" data-tooltip-content="Like" className="p-1.5 text-gray-400 hover:text-white rounded-md hover:bg-gray-700">
                <ThumbsUp className="w-4 h-4" />
              </button>
              <button data-tooltip-id="dislike-tooltip" data-tooltip-content="Dislike" className="p-1.5 text-gray-400 hover:text-white rounded-md hover:bg-gray-700">
                <ThumbsDown className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </motion.div>
      <Tooltip id="copy-tooltip" />
      <Tooltip id="like-tooltip" />
      <Tooltip id="dislike-tooltip" />
    </AnimatePresence>
  );
};

export default ChatMessage;
