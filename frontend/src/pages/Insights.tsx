import { BarChart3, Code2, FileText, PieChart } from "lucide-react";
import { EmptyState, Page, Panel, SectionTitle, StatusPill } from "../components/ui";
import { useAnalysis } from "../state/analysis-store";
import { motion } from "framer-motion";
import { cx } from "../lib/format";

export function Insights() {
  const { github, resume, comparison } = useAnalysis();
  const languageTotal = Object.values(github?.language_totals ?? {}).reduce((sum, value) => sum + value, 0) || 1;

  return (
    <Page>
      <div className="mb-12">
        <StatusPill tone="blue">Data Intelligence</StatusPill>
        <h1 className="mt-4 text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          Deep <span className="text-accent">Verification.</span>
        </h1>
        <p className="mt-4 max-w-2xl text-lg font-medium text-muted leading-relaxed">
          Granular breakdown of your technical footprint across GitHub and professional documentation.
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr_1fr]">
        <Panel>
          <SectionTitle 
            kicker="Code Footprint" 
            title="Language Intel" 
            description="The composition of your public code history by byte-weight across all analyzed repositories."
            action={<div className="p-2 rounded-xl bg-accent/10 text-accent"><BarChart3 size={20} /></div>} 
          />
          {github ? (
            <div className="space-y-6">
              {Object.entries(github.language_totals).slice(0, 8).map(([language, bytes], index) => (
                <motion.div 
                  key={language}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-bold text-ink">{language}</span>
                    <span className="text-xs font-bold text-muted uppercase tracking-widest">{Math.round((bytes / languageTotal) * 100)}%</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded-full bg-slate-50 ring-1 ring-line">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.max(4, (bytes / languageTotal) * 100)}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className="h-full rounded-full bg-accent" 
                    />
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <EmptyState icon={PieChart} title="No GitHub data" body="Run an analysis to see language and evidence distribution." />
          )}
        </Panel>

        <Panel>
          <SectionTitle 
            kicker="Documentation" 
            title="Project Evidence" 
            description="Deep-extracted projects from your resume and their associated technical stacks."
            action={<div className="p-2 rounded-xl bg-blue-500/10 text-blue-500"><FileText size={20} /></div>} 
          />
          {resume ? (
            <div className="space-y-4">
              {resume.projects.length ? (
                resume.projects.map((project, index) => (
                  <motion.article 
                    key={project.name} 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="group rounded-2xl border border-line p-5 transition-all hover:border-accent/30 hover:bg-slate-50"
                  >
                    <p className="font-bold text-ink group-hover:text-accent transition-colors">{project.name}</p>
                    <p className="mt-3 text-sm font-medium leading-relaxed text-muted">{project.description}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {project.skills.map((skill) => (
                        <span key={skill} className="rounded-lg bg-white px-2.5 py-1 text-[10px] font-bold text-ink ring-1 ring-line shadow-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </motion.article>
                ))
              ) : (
                <EmptyState title="No projects extracted" body="The resume parser found skills but no explicit project blocks." />
              )}
            </div>
          ) : (
            <EmptyState title="No resume data" body="Upload a PDF resume to see project-backed claims." />
          )}
        </Panel>
      </div>

      <div className="mt-8">
        <Panel>
          <SectionTitle 
            kicker="Summary" 
            title="Evidence Equilibrium" 
            description="High-level balance of your technical narrative across all verified channels."
            action={<div className="p-2 rounded-xl bg-amber-500/10 text-amber-500"><Code2 size={20} /></div>} 
          />
          {comparison ? (
            <div className="grid gap-6 md:grid-cols-3">
              <InsightCount label="Verified Skills" value={comparison.verified_skills.length} color="text-accent" />
              <InsightCount label="Unproven Claims" value={comparison.claimed_unproven_skills.length} color="text-amber-500" />
              <InsightCount label="Critical Gaps" value={comparison.missing_skills.length} color="text-rose-500" />
            </div>
          ) : (
            <EmptyState title="No comparison data" body="SkillLens will summarize verified, unproven, and missing skills after analysis." />
          )}
        </Panel>
      </div>
    </Page>
  );
}

function InsightCount({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="rounded-[2.5rem] border border-line bg-slate-50/50 p-8 text-center transition-all hover:bg-white hover:shadow-soft">
      <p className="text-[10px] font-bold uppercase tracking-widest text-muted">{label}</p>
      <p className={cx("mt-4 text-6xl font-black tracking-tighter", color)}>{value}</p>
    </div>
  );
}
