"use client";

import { useState } from "react";
import {
  useFloating,
  autoUpdate,
  offset,
  flip,
  shift,
  useHover,
  useFocus,
  useDismiss,
  useRole,
  useInteractions,
  FloatingPortal,
} from "@floating-ui/react";
import { motion, AnimatePresence } from "framer-motion";
import { BrainCircuit, Database, Network } from "lucide-react";

interface ReasoningPopoverProps {
  graphContext: string;
  vectorContext: string;
}

export default function ReasoningPopover({ graphContext, vectorContext }: ReasoningPopoverProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { refs, floatingStyles, context } = useFloating({
    open: isOpen,
    onOpenChange: setIsOpen,
    middleware: [offset(10), flip(), shift()],
    whileElementsMounted: autoUpdate,
  });

  const hover = useHover(context, { move: false });
  const focus = useFocus(context);
  const dismiss = useDismiss(context);
  const role = useRole(context, { role: "tooltip" });

  const { getReferenceProps, getFloatingProps } = useInteractions([
    hover,
    focus,
    dismiss,
    role,
  ]);

  return (
    <>
      <button
        ref={refs.setReference}
        {...getReferenceProps()}
        className="flex items-center gap-2 text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors bg-blue-950/30 px-3 py-1.5 rounded-full border border-blue-800/50 hover:bg-blue-900/50"
      >
        <BrainCircuit className="w-3.5 h-3.5" />
        View Reasoning
      </button>
      <FloatingPortal>
        <AnimatePresence>
          {isOpen && (
            <motion.div
              ref={refs.setFloating}
              style={floatingStyles}
              {...getFloatingProps()}
              initial={{ opacity: 0, scale: 0.95, y: 5 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 5 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="z-50 max-w-md w-full bg-slate-900/95 backdrop-blur-xl border border-slate-700/50 rounded-xl shadow-2xl p-4 text-slate-200 overflow-hidden ring-1 ring-white/10"
            >
              <div className="space-y-4">
                <div>
                  <div className="flex items-center gap-2 text-emerald-400 mb-2">
                    <Network className="w-4 h-4" />
                    <h4 className="font-semibold text-sm uppercase tracking-wider">Knowledge Graph</h4>
                  </div>
                  <div className="text-xs bg-slate-950/50 p-3 rounded-lg border border-slate-800 font-mono text-slate-400 max-h-32 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                    {graphContext || "No graph context found."}
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-2 text-purple-400 mb-2">
                    <Database className="w-4 h-4" />
                    <h4 className="font-semibold text-sm uppercase tracking-wider">Medical Guidelines</h4>
                  </div>
                  <div className="text-xs bg-slate-950/50 p-3 rounded-lg border border-slate-800 font-mono text-slate-400 max-h-32 overflow-y-auto whitespace-pre-wrap scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                    {vectorContext || "No guidelines found."}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </FloatingPortal>
    </>
  );
}
