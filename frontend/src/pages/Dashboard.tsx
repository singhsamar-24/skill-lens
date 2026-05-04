import { motion } from "framer-motion";
import { AlertCircle, Code2, Github, Trophy } from "lucide-react";
import { AnalysisForm } from "../components/AnalysisForm";
import { InsightPanel } from "../components/InsightPanel";
import { SkillBadge } from "../components/SkillBadge";
import { SkillDistribution } from "../components/SkillDistribution";
import { StatusRail } from "../components/StatusRail";
import { TrustScoreCard } from "../components/TrustScoreCard";
import { EmptyState, Page, Panel, SectionTitle, SkeletonBlock, StatusPill } from "../components/ui";
import { compactNumber, cx } from "../lib/format";
import { useAnalysis } from "../state/analysis-store";

export function Dashboard() {
  const { github, resume, leetcode, codeforces, comparison, statuses, errors } = useAnalysis();
  const loading = Object.values(statuses).some((status) => status === "loading");

  return (
    <Page>
      <div className="mb-12 grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <StatusPill tone="blue">Verification Intelligence</StatusPill>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-ink sm:text-5xl lg:text-6xl">
            Real Evidence. <br /><span className="text-accent">Zero Friction.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
            Upload your resume and connect your GitHub profile. SkillLens cross-references your claims with real-world contributions to build a trustable profile.
          </p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="rounded-[2.5rem] border border-line bg-white/40 p-2 shadow-soft backdrop-blur-xl"
        >
          <div className="rounded-[2.2rem] bg-white p-2">
            <AnalysisForm compact />
          </div>
        </motion.div>
      </div>

      <StatusRail />

      {errors.length ? (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-8">
          <Panel className="border-red-100 bg-red-50/50">
            <div className="flex items-center gap-3 text-red-700">
              <AlertCircle size={20} />
              <p className="font-bold">System Attention Needed</p>
            </div>
            <ul className="mt-3 space-y-1 pl-8 text-sm text-red-600/80">
              {errors.map((error) => (
                <li key={error} className="list-disc">{error}</li>
              ))}
            </ul>
          </Panel>
        </motion.div>
      ) : null}

      <div className="mt-12 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <TrustScoreCard comparison={comparison} />
        <div className="grid gap-6">
          <SkillDistribution comparison={comparison} />
          <InsightPanel comparison={comparison} />
        </div>
      </div>

      <div className="mt-12 grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <Panel>
          <SectionTitle 
            kicker="Evidence Engine" 
            title="GitHub Proofs" 
            description="Verified skills extracted from your recent code commits and repository activity."
          />
          {statuses.github === "loading" ? <SkillSkeleton /> : null}
          {github ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {github.skills.slice(0, 8).map((skill, index) => (
                <motion.div 
                  key={skill.normalized} 
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }} 
                  transition={{ duration: 0.4, delay: index * 0.05 }}
                >
                  <SkillBadge skill={skill} />
                </motion.div>
              ))}
            </div>
          ) : !loading ? (
            <EmptyState icon={Github} title="No GitHub analysis yet" body="Run SkillLens with a username and resume to see evidence-backed skills." />
          ) : null}
        </Panel>

        <Panel>
          <SectionTitle 
            kicker="Extraction" 
            title="Resume Claims" 
            description="Skills and experiences identified in your uploaded professional profile."
          />
          {statuses.resume === "loading" ? <SkillSkeleton /> : null}
          {resume ? (
            <div className="space-y-4">
              {resume.skills.slice(0, 10).map((skill) => (
                <div key={skill.normalized} className="group rounded-2xl border border-line p-5 transition-all hover:border-accent/30 hover:bg-slate-50/50">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-bold text-ink">{skill.name}</p>
                      <p className="mt-1 text-xs text-muted font-medium">{skill.evidence[0] ?? "Resume mention"}</p>
                    </div>
                    <StatusPill tone={skill.classification === "project_backed" ? "good" : skill.classification === "claimed" ? "warn" : "neutral"}>
                      {skill.classification}
                    </StatusPill>
                  </div>
                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.max(4, Math.round(skill.confidence * 100))}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className="h-full rounded-full bg-accent" 
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : !loading ? (
            <EmptyState title="No resume analysis yet" body="Upload a PDF resume to extract claimed and project-backed skills." />
          ) : null}
        </Panel>
      </div>

      <div className="mt-12 grid gap-8 lg:grid-cols-2">
        <Panel>
          <SectionTitle kicker="Deep Scan" title="Repository Intel" description="The most impactful projects analyzed during verification." />
          {github ? (
            <div className="space-y-4">
              {github.analyzed_repos.slice(0, 6).map((repo) => (
                <a
                  key={repo.full_name}
                  href={repo.url}
                  target="_blank"
                  rel="noreferrer"
                  className="group block rounded-2xl border border-line p-5 transition-all hover:border-accent/40 hover:bg-slate-50 hover:shadow-soft"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="font-bold text-ink group-hover:text-accent transition-colors">{repo.full_name}</p>
                      <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-muted font-medium">{repo.description ?? repo.readme_excerpt ?? "Repository evidence analyzed"}</p>
                    </div>
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-50 text-accent group-hover:bg-accent group-hover:text-white transition-all">
                      <Code2 size={20} />
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {Object.keys(repo.languages).slice(0, 4).map(lang => (
                      <span key={lang} className="text-[10px] font-bold uppercase tracking-wider text-muted/60">{lang}</span>
                    ))}
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <EmptyState title="Repositories will appear here" body="SkillLens limits repository reads to stay friendly to GitHub API budgets." />
          )}
        </Panel>

        <Panel>
          <SectionTitle kicker="Algorithmic" title="LeetCode Signal" description="Competitive programming signals from your LeetCode profile." />
          {leetcode?.status === "ok" ? (
            <div className="space-y-8">
              <div className="grid grid-cols-3 gap-4">
                <MetricMini label="Easy" value={leetcode.easy_solved} color="text-emerald-500" />
                <MetricMini label="Medium" value={leetcode.medium_solved} color="text-amber-500" />
                <MetricMini label="Hard" value={leetcode.hard_solved} color="text-rose-500" />
              </div>
              <div>
                <p className="mb-4 text-xs font-bold uppercase tracking-widest text-muted">Topic Proficiency</p>
                <div className="flex flex-wrap gap-2">
                  {leetcode.topics.slice(0, 10).map((topic) => (
                    <span key={topic.topic} className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-bold text-ink transition-colors hover:bg-accent hover:text-white">
                      {topic.topic}: <span className="opacity-60">{compactNumber(topic.solved)}</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <EmptyState title="Optional signal" body={leetcode?.warning ?? "Add a LeetCode username to include solved count, difficulty mix, and topics."} />
          )}
        </Panel>

        <Panel>
          <SectionTitle kicker="Competitive" title="Codeforces Signal" description="Contest history and accepted problem coverage from your Codeforces handle." />
          {codeforces?.status === "ok" ? (
            <div className="space-y-8">
              <div className="grid grid-cols-3 gap-4">
                <MetricMini label="Solved" value={codeforces.solved_count} color="text-emerald-500" />
                <MetricMini label="Rating" value={codeforces.rating ?? 0} color="text-sky-500" />
                <MetricMini label="Contests" value={codeforces.contests} color="text-violet-500" />
              </div>
              <div className="rounded-2xl border border-line bg-slate-50/50 p-5">
                <div className="flex items-center gap-3">
                  <div className="grid h-10 w-10 place-items-center rounded-xl bg-white text-accent">
                    <Trophy size={18} />
                  </div>
                  <div>
                    <p className="font-bold text-ink">{codeforces.handle ?? codeforces.username}</p>
                    <p className="text-sm font-medium text-muted">
                      {codeforces.rank ?? "unrated"} · max {codeforces.max_rating ?? codeforces.rating ?? "unrated"}
                    </p>
                  </div>
                </div>
              </div>
              <div>
                <p className="mb-4 text-xs font-bold uppercase tracking-widest text-muted">Accepted Tags</p>
                <div className="flex flex-wrap gap-2">
                  {codeforces.topics.slice(0, 10).map((topic) => (
                    <span key={topic.topic} className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-bold text-ink transition-colors hover:bg-accent hover:text-white">
                      {topic.topic}: <span className="opacity-60">{compactNumber(topic.solved)}</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <EmptyState title="Optional signal" body={codeforces?.warning ?? "Add a Codeforces handle to include contests, rating, solved count, and accepted tags."} />
          )}
        </Panel>
      </div>
    </Page>
  );
}

function SkillSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[0, 1, 2, 3].map((item) => (
        <SkeletonBlock key={item} className="h-32" />
      ))}
    </div>
  );
}

function MetricMini({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="rounded-2xl border border-line bg-slate-50/50 p-5 transition-all hover:bg-white hover:shadow-soft">
      <p className="text-[10px] font-bold uppercase tracking-widest text-muted">{label}</p>
      <p className={cx("mt-3 text-3xl font-bold tracking-tight", color)}>{value}</p>
    </div>
  );
}
