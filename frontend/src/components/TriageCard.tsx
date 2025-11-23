"use client";

import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle, Clock, Activity } from "lucide-react";
import clsx from "clsx";
import ReasoningPopover from "./ReasoningPopover";

interface TriageCardProps {
  diagnosis: string;
  triageLevel: string;
  reasoning: string;
  graphContext?: string;
  vectorContext?: string;
}

export default function TriageCard({ diagnosis, triageLevel, reasoning, graphContext, vectorContext }: TriageCardProps) {
  const isEmergency = triageLevel.toLowerCase().includes("emergency");
  const isUrgent = triageLevel.toLowerCase().includes("urgent") && !isEmergency;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={clsx(
        "w-full rounded-2xl border p-6 shadow-lg backdrop-blur-sm mt-4",
        isEmergency ? "bg-red-950/10 border-red-500/20 shadow-red-900/10" :
          isUrgent ? "bg-amber-950/10 border-amber-500/20 shadow-amber-900/10" :
            "bg-emerald-950/10 border-emerald-500/20 shadow-emerald-900/10"
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={clsx(
            "p-2 rounded-lg",
            isEmergency ? "bg-red-500/10 text-red-400" :
              isUrgent ? "bg-amber-500/10 text-amber-400" :
                "bg-emerald-500/10 text-emerald-400"
          )}>
            {isEmergency ? <AlertTriangle className="w-6 h-6" /> :
              isUrgent ? <Clock className="w-6 h-6" /> :
                <CheckCircle className="w-6 h-6" />}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-100">{diagnosis}</h3>
            <span className={clsx(
              "text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border",
              isEmergency ? "bg-red-500/10 border-red-500/20 text-red-400" :
                isUrgent ? "bg-amber-500/10 border-amber-500/20 text-amber-400" :
                  "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
            )}>
              {triageLevel}
            </span>
          </div>
        </div>
      </div>

      <p className="text-slate-300 leading-relaxed mb-6 text-sm">
        {reasoning}
      </p>

      <div className="flex items-center justify-between pt-4 border-t border-slate-700/30">
        <div className="flex items-center gap-2 text-slate-500 text-xs">
          <Activity className="w-4 h-4" />
          <span>AI Analysis Complete</span>
        </div>

        {(graphContext || vectorContext) && (
          <ReasoningPopover graphContext={graphContext || ""} vectorContext={vectorContext || ""} />
        )}
      </div>
    </motion.div>
  );
}
