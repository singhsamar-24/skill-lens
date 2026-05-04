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

export interface CodeforcesAnalysis {
  username: string;
  status: "ok" | "unavailable";
  handle?: string | null;
  rank?: string | null;
  rating?: number | null;
  max_rank?: string | null;
  max_rating?: number | null;
  contribution?: number | null;
  friend_of_count?: number | null;
  contests: number;
  solved_count: number;
  attempted_count: number;
  accepted_submissions: number;
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

export interface MarketCompanyRoadmap {
  company: string;
  fit: number;
  salary: string;
  apply_link?: string | null;
  process: string[];
  gaps: string[];
  prep_plan: string[];
  question_themes: string[];
}

export interface MarketRoadmapResponse {
  companies: MarketCompanyRoadmap[];
}

export interface MentorChatResponse {
  routed_sources: RagSource[];
  route_reason: string;
  answer: string;
  citations: string[];
  snippets: { source: RagSource; source_label: string; title: string; text: string; score: number; chunk_id: string; metadata: Record<string, unknown> }[];
}

export interface RecruiterCandidateSummary {
  id: number;
  name: string;
  email?: string | null;
  github_username?: string | null;
  skills: ResumeSkill[];
}

export interface RecruiterUploadResponse {
  uploaded: number;
  candidates: RecruiterCandidateSummary[];
}

export interface RecruiterEvaluationResult {
  candidate_id: number;
  name: string;
  email?: string | null;
  github_username?: string | null;
  target_role: string;
  match_score: number;
  verified_skills: ComparedSkill[];
  missing_skills: CompareResponse["missing_skills"];
  explanations: {
    insights?: CompareResponse["insights"];
    recommendations?: string[];
    claimed_unproven_skills?: ComparedSkill[];
    github_only_skills?: ComparedSkill[];
    problem_solving_signal?: string;
    evidence_score?: number;
    role_fit_score?: number;
  };
  role_matches: CompareResponse["career_matches"];
}

export interface RecruiterEvaluateResponse {
  target_role: string;
  evaluated: number;
  results: RecruiterEvaluationResult[];
}

export interface RecruiterRankItem {
  rank: number;
  candidate_id: number;
  name: string;
  email?: string | null;
  github_username?: string | null;
  target_role: string;
  match_score: number;
  top_verified_skills: string[];
  top_missing_skills: string[];
  recommendation: Priority;
  explanations: RecruiterEvaluationResult["explanations"];
}

export interface RecruiterRankResponse {
  target_role?: string | null;
  candidates: RecruiterRankItem[];
}
