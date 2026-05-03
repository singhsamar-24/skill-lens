export type SkillLevel = "strong" | "moderate" | "exposure";
export type ResumeSkillLevel = "claimed" | "project_backed" | "weak";
export type Priority = "high" | "medium" | "low";
export type RagSource = "alumni" | "learning" | "job";

export interface EvidenceItem {
  source: string;
  detail: string;
  url?: string | null;
  weight: number;
}

export interface SkillCredibility {
  score: number;
  repo_count: number;
  commit_count: number;
  recent_repo_count: number;
  language_share: number;
  last_seen_at?: string | null;
}

export interface SkillEvidence {
  name: string;
  normalized: string;
  level: SkillLevel;
  confidence: number;
  credibility?: SkillCredibility;
  evidence: EvidenceItem[];
}

export interface ResumeSkill {
  name: string;
  normalized: string;
  classification: ResumeSkillLevel;
  confidence: number;
  evidence: string[];
}

export interface WarningMessage {
  code: string;
  message: string;
}

export interface RepositoryEvidence {
  name: string;
  full_name: string;
  url: string;
  description?: string | null;
  stars: number;
  forks: number;
  pushed_at?: string | null;
  languages: Record<string, number>;
  topics: string[];
  readme_excerpt?: string | null;
  commits: { message: string; url: string; date?: string | null }[];
}

export interface GitHubAnalysis {
  username: string;
  profile_url: string;
  avatar_url?: string | null;
  public_repos: number;
  analyzed_repos: RepositoryEvidence[];
  language_totals: Record<string, number>;
  skills: SkillEvidence[];
  warnings: WarningMessage[];
  rate_limit?: { remaining?: number | null; reset_epoch?: number | null; resource?: string | null } | null;
}

export interface ResumeAnalysis {
  file_name: string;
  text_preview: string;
  skills: ResumeSkill[];
  projects: { name: string; description: string; skills: string[] }[];
  warnings: WarningMessage[];
}

export interface LeetCodeAnalysis {
  username: string;
  status: "ok" | "unavailable";
  total_solved: number;
  easy_solved: number;
  medium_solved: number;
  hard_solved: number;
  ranking?: number | null;
  topics: { topic: string; solved: number }[];
  problem_solving_signal: "strong" | "moderate" | "emerging" | "unknown";
  warning?: string | null;
}

export interface ComparedSkill {
  name: string;
  confidence: number;
  resume_signal?: string | null;
  github_signal?: string | null;
  evidence: Array<EvidenceItem | string>;
}

export interface CompareResponse {
  target_role: string;
  verified_skills: ComparedSkill[];
  claimed_unproven_skills: ComparedSkill[];
  github_only_skills: ComparedSkill[];
  missing_skills: { name: string; priority: Priority; reason: string; usage: string[]; impact: string }[];
  career_matches: { role: string; match: number; salary: string; reason: string; matched_skills: string[]; missing_skills: string[] }[];
  evidence_score: number;
  problem_solving_signal: string;
  insights: { type: "over_claim" | "under_sell" | "strength" | "gap" | "proof"; title: string; detail: string; severity: Priority }[];
  recommendations: string[];
}

export interface RoadmapResponse {
  target_role: string;
  focus_skills: { skill: string; priority: Priority; rationale: string }[];
  milestones: { week: string; title: string; tasks: string[]; project: string; outcomes: string[] }[];
  portfolio_projects: string[];
  mentor_note: string;
}

export interface MentorChatResponse {
  routed_sources: RagSource[];
  route_reason: string;
  answer: string;
  citations: string[];
  snippets: { source: RagSource; source_label: string; title: string; text: string; score: number; chunk_id: string; metadata: Record<string, unknown> }[];
}
