"use client";

import { Plus, Search, Book, FolderOpen, Puzzle, Compass, MessageSquare, X } from "lucide-react";
import { motion } from "framer-motion";

interface SidebarProps {
    isOpen: boolean;
    toggleSidebar: () => void;
    onNewChat: () => void;
}

export default function Sidebar({ isOpen, toggleSidebar, onNewChat }: SidebarProps) {
    if (!isOpen) return null;

    const navItems = [
        { icon: MessageSquare, label: "New chat", onClick: onNewChat },
        { icon: Search, label: "Search chats" },
        { icon: Book, label: "Library" },
        { icon: FolderOpen, label: "Projects" },
    ];

    const chatHistory = [
        "Graph database integration",
        "Update Discord on Arch",
        "AWS lambda path query",
        "Zceker restrictions impact...",
        "Installation request template",
        "Business analyst demand a...",
        "Casual conversation respo...",
        "Resume improvement tips",
        "Kafka producer best pract...",
        "Curl empty reply issue",
        "Greeting exchange",
        "Remainder of 3/100 mod 7",
        "Modularizing Nx monorepo",
        "Enable Gemini API",
    ];

    return (
        <div className="w-64 h-screen bg-[#2a2b2e] border-r border-[#3c3d3f] flex flex-col fixed left-0 top-0 z-50">
            {/* New Chat Button */}
            <div className="p-2">
                <button
                    onClick={onNewChat}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border border-[#3c3d3f] bg-transparent text-[#ececf1] hover:bg-[#343541] transition-colors"
                    title="Start a new chat"
                >
                    <Plus className="w-4 h-4" />
                    <span className="text-sm font-medium font-inter">New chat</span>
                </button>
            </div>

            {/* Navigation Section */}
            <div className="px-2 py-2">
                {navItems.map((item, idx) => (
                    <button
                        key={idx}
                        onClick={item.onClick}
                        className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[#ececf1] hover:bg-[#343541] transition-colors mb-1"
                        title={item.label}
                    >
                        <item.icon className="w-4 h-4 text-[#8e8e90]" />
                        <span className="text-sm font-lato">{item.label}</span>
                    </button>
                ))}
            </div>

            {/* GPTs Section */}
            <div className="px-2 py-2">
                <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[#ececf1] hover:bg-[#343541] transition-colors" title="Explore GPTs">
                    <Puzzle className="w-4 h-4 text-[#8e8e90]" />
                    <span className="text-sm font-lato">GPTs</span>
                </button>
                <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[#ececf1] hover:bg-[#343541] transition-colors" title="Explore">
                    <Compass className="w-4 h-4 text-[#8e8e90]" />
                    <span className="text-sm font-lato">Explore</span>
                </button>
            </div>

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto px-2 py-2">
                <div className="text-xs font-semibold text-[#8e8e90] px-3 py-2 mb-1 font-inter">Your chats</div>
                {chatHistory.map((chat, idx) => (
                    <motion.button
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[#ececf1] hover:bg-[#343541] transition-colors mb-1 text-left"
                        title={chat}
                    >
                        <MessageSquare className="w-4 h-4 text-[#8e8e90] flex-shrink-0" />
                        <span className="text-sm truncate font-lato">{chat}</span>
                    </motion.button>
                ))}
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-[#3c3d3f]">
                <button className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-[#343541] transition-colors" title="User profile">
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center text-xs font-medium text-white">
                            JK
                        </div>
                        <span className="text-sm text-[#ececf1] font-lato">Jai Krishna</span>
                    </div>
                </button>
                <button className="w-full mt-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-medium rounded-full hover:opacity-90 transition-opacity font-inter" title="Upgrade to Pro">
                    Upgrade
                </button>
            </div>

            {/* Close button for mobile */}
            <button
                onClick={toggleSidebar}
                className="absolute top-3 right-3 p-2 text-[#8e8e90] hover:text-[#ececf1] hover:bg-[#343541] rounded-lg transition-colors md:hidden"
                title="Close sidebar"
            >
                <X className="w-5 h-5" />
            </button>
        </div>
    );
}
