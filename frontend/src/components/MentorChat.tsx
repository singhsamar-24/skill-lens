import { useState } from "react";
import { Bot, Send, UserRound, Sparkles } from "lucide-react";
import { api } from "../lib/api";
import { cx } from "../lib/format";
import { useAnalysis } from "../state/analysis-store";
import type { MentorChatResponse } from "../types";
import { Button, StatusPill } from "./ui";
import { motion, AnimatePresence } from "framer-motion";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  meta?: MentorChatResponse;
}

function messageId() {
  return typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
}

export function MentorChat() {
  const { comparison, github, resume, leetcode, targetRole } = useAnalysis();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "intro",
      role: "assistant",
      content: "Hello! I'm your Career Mentor. Ask me about career gaps, learning sequences, role expectations, or how to turn your evidence into a stronger narrative.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sourceMode, setSourceMode] = useState<"auto" | "alumni" | "learning" | "job">("auto");

  async function send(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = input.trim();
    if (!text || loading) return;
    setMessages((current) => [...current, { id: messageId(), role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const response = await api.mentor({
        message: text,
        sources: sourceMode === "auto" ? "auto" : [sourceMode],
        profile_context: {
          targetRole,
          evidenceScore: comparison?.evidence_score,
          verifiedSkills: comparison?.verified_skills.map((skill) => skill.name),
          missingSkills: comparison?.missing_skills.map((skill) => skill.name),
          githubUser: github?.username,
          resumeSkills: resume?.skills.map((skill) => skill.normalized),
          leetcodeSignal: leetcode?.problem_solving_signal,
        },
      });
      setMessages((current) => [...current, { id: messageId(), role: "assistant", content: response.answer, meta: response }]);
    } catch (error) {
      setMessages((current) => [...current, { id: messageId(), role: "assistant", content: (error as Error).message }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[700px] flex-col overflow-hidden rounded-[2.5rem] border border-line bg-white shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line bg-slate-50/50 p-6 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-ink text-white shadow-lg">
            <Bot size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-ink">Verification Mentor</h2>
            <div className="flex items-center gap-2 mt-0.5">
               <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
               <p className="text-xs font-bold text-muted uppercase tracking-widest">AI Engine Active</p>
            </div>
          </div>
        </div>
        <div className="flex rounded-xl bg-white p-1 shadow-sm ring-1 ring-line">
          {(["auto", "alumni", "learning", "job"] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setSourceMode(mode)}
              className={cx(
                "h-9 rounded-lg px-4 text-xs font-bold capitalize transition-all",
                sourceMode === mode ? "bg-ink text-white shadow-md" : "text-muted hover:bg-slate-50 hover:text-ink",
              )}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex-1 space-y-6 overflow-y-auto p-6 bg-[#FDFDFE]">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.article 
              key={message.id} 
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              className={cx("flex gap-4", message.role === "user" && "flex-row-reverse")}
            >
              <div className={cx(
                "flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl shadow-sm",
                message.role === "assistant" ? "bg-white text-ink border border-line" : "bg-accent text-white"
              )}>
                {message.role === "assistant" ? <Bot size={20} /> : <UserRound size={20} />}
              </div>
              
              <div className={cx(
                "group relative max-w-[80%] rounded-[2rem] p-6 text-sm leading-relaxed",
                message.role === "user" 
                  ? "bg-ink text-white rounded-tr-none shadow-xl" 
                  : "bg-white text-ink border border-line rounded-tl-none shadow-soft"
              )}>
                <p className="whitespace-pre-line font-medium">{message.content}</p>
                
                {message.meta ? (
                  <div className="mt-6 space-y-4">
                    <div className="flex flex-wrap gap-2">
                      {message.meta.routed_sources.map((source) => (
                        <StatusPill key={source} tone={source === "learning" ? "good" : source === "job" ? "warn" : "neutral"}>
                          {source}
                        </StatusPill>
                      ))}
                    </div>
                    
                    {message.meta.route_reason && (
                      <div className="rounded-2xl border border-line bg-slate-50/50 p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Sparkles size={12} className="text-accent" />
                          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-muted">Routing Logic</p>
                        </div>
                        <p className="text-xs font-medium leading-relaxed text-muted">{message.meta.route_reason}</p>
                      </div>
                    )}
                    
                    <div className="grid gap-3">
                      {message.meta.snippets.slice(0, 3).map((snippet) => (
                        <div key={snippet.chunk_id} className="group/snippet rounded-2xl border border-line bg-white p-4 transition-all hover:border-accent/30 hover:shadow-sm">
                          <div className="flex items-center justify-between gap-3 mb-2">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-accent">{snippet.source_label}</p>
                            <span className="text-[10px] font-bold text-muted opacity-40">{snippet.score.toFixed(2)}</span>
                          </div>
                          <p className="text-xs font-bold text-ink mb-1">{snippet.title}</p>
                          <p className="text-xs font-medium leading-relaxed text-muted line-clamp-2">{snippet.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            </motion.article>
          ))}
        </AnimatePresence>
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white text-ink border border-line shadow-sm">
              <Bot size={20} />
            </div>
            <div className="bg-white border border-line rounded-[2rem] rounded-tl-none p-6 shadow-soft">
               <div className="flex gap-1.5">
                  <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300" />
                  <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300 [animation-delay:0.2s]" />
                  <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300 [animation-delay:0.4s]" />
               </div>
            </div>
          </motion.div>
        )}
      </div>

      <div className="border-t border-line bg-white p-6">
        <form onSubmit={send} className="relative flex items-center gap-3">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about your next career step..."
            className="h-14 w-full rounded-2xl border border-line bg-slate-50 px-6 pr-24 text-sm font-medium shadow-sm transition-all placeholder:text-slate-400 focus:border-accent focus:bg-white focus:ring-4 focus:ring-accent/5 outline-none"
          />
          <div className="absolute right-2">
            <Button 
              type="submit" 
              disabled={loading || !input.trim()}
              className="h-10 px-4 rounded-xl shadow-lg"
            >
              <Send size={16} />
              <span className="hidden sm:inline">Send</span>
            </Button>
          </div>
        </form>
        <p className="mt-4 text-center text-[10px] font-medium text-muted uppercase tracking-widest">
           RAG-Enhanced Mentorship System • Connected to global knowledge bases
        </p>
      </div>
    </div>
  );
}
