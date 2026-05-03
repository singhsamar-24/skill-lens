import { useState, useEffect } from "react";
import { ArrowRight, Github, Target } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAnalysis } from "../state/analysis-store";
import { Button } from "./ui";
import { UploadDropzone } from "./UploadDropzone";
import { motion } from "framer-motion";

export function AnalysisForm({ compact = false }: { compact?: boolean }) {
  const navigate = useNavigate();
  const { runAnalysis, statuses } = useAnalysis();
  const [githubUsername, setGithubUsername] = useState("");
  const [leetcodeUsername, setLeetcodeUsername] = useState("");
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [resumeFile, setResumeFile] = useState<File>();
  const loading = Object.values(statuses).some((status) => status === "loading");

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!resumeFile || !githubUsername.trim()) return;
    navigate("/dashboard");
    await runAnalysis({ githubUsername: githubUsername.trim(), leetcodeUsername: leetcodeUsername.trim(), targetRole, resumeFile });
  }

  const inputClasses = "h-14 w-full rounded-2xl border border-transparent bg-slate-50 px-5 text-base font-medium transition-all placeholder:text-slate-400 hover:bg-slate-100 focus:border-ink/20 focus:bg-white focus:shadow-xl focus:outline-none";

  return (
    <form onSubmit={submit} className={`grid gap-6 ${compact ? '' : 'lg:grid-cols-2'}`}>
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-muted">
          <Github size={14} />
          GitHub Handle
        </label>
        <input
          value={githubUsername}
          onChange={(event) => setGithubUsername(event.target.value)}
          placeholder="e.g. octocat"
          className={inputClasses}
          required
        />
      </div>
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-muted">
          <Target size={14} />
          Target Role
        </label>
        <input
          value={targetRole}
          onChange={(event) => setTargetRole(event.target.value)}
          placeholder="e.g. Senior Frontend Engineer"
          className={inputClasses}
        />
      </div>
      <div className={`${compact ? '' : 'lg:col-span-2'} space-y-3`}>
        <label className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-muted">
          Professional Resume
        </label>
        <UploadDropzone file={resumeFile} onChange={setResumeFile} />
      </div>
      
      <div className={`${compact ? '' : 'lg:col-span-2'} space-y-3`}>
        <label className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-muted">
          LeetCode Profile <span className="opacity-50">(Optional)</span>
        </label>
        <input
          value={leetcodeUsername}
          onChange={(event) => setLeetcodeUsername(event.target.value)}
          placeholder="username"
          className={inputClasses}
        />
      </div>

      <div className={`${compact ? '' : 'lg:col-span-2'} pt-6`}>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button 
            type="submit" 
            disabled={loading || !resumeFile || !githubUsername.trim()} 
            className="h-16 w-full rounded-2xl bg-ink text-base font-bold tracking-wide text-white shadow-2xl transition-all hover:bg-slate-800 disabled:opacity-30 disabled:hover:scale-100"
          >
            {loading ? (
              <span className="flex items-center gap-3">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white" />
                Initializing Analysis...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Commence Verification
                <ArrowRight size={18} />
              </span>
            )}
          </Button>
        </motion.div>
        <p className="mt-6 text-center text-[10px] font-bold uppercase tracking-widest text-muted/60">
          Secure Processing • End-to-End Encryption
        </p>
      </div>
    </form>
  );
}
