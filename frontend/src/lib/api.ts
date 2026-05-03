import type {
  CompareResponse,
  GitHubAnalysis,
  LeetCodeAnalysis,
  MentorChatResponse,
  ResumeAnalysis,
  RoadmapResponse,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface ApiErrorBody {
  detail?: {
    code?: string;
    message?: string;
  };
}

async function requestJson<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> ?? {}),
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  } else {
    const savedToken = localStorage.getItem("skilllens_token");
    if (savedToken) {
      headers["Authorization"] = `Bearer ${savedToken}`;
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    throw new Error(body.detail?.message ?? "SkillLens request failed.");
  }
  return (await response.json()) as T;
}

export const api = {
  health: () => requestJson<{ status: string; rag_ready: boolean; groq_configured: boolean; rag_backend: string }>("/health"),
  getMe: (token: string) => requestJson<{ username: string; email?: string; avatar?: string }>("/api/auth/me", {}, token),
  analyzeGitHub: (username: string) =>
    requestJson<GitHubAnalysis>("/api/github/analyze", {
      method: "POST",
      body: JSON.stringify({ username }),
    }),
  analyzeResume: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    const token = localStorage.getItem("skilllens_token");
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE}/api/resume/analyze`, {
      method: "POST",
      body: form,
      headers
    });
    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
      throw new Error(body.detail?.message ?? "Resume analysis failed.");
    }
    return (await response.json()) as ResumeAnalysis;
  },
  analyzeLeetCode: (username: string) =>
    requestJson<LeetCodeAnalysis>("/api/leetcode/analyze", {
      method: "POST",
      body: JSON.stringify({ username }),
    }),
  compare: (payload: { github: GitHubAnalysis; resume: ResumeAnalysis; leetcode?: LeetCodeAnalysis | null; target_role?: string }) =>
    requestJson<CompareResponse>("/api/compare", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  roadmap: (payload: { comparison: CompareResponse; target_role: string }) =>
    requestJson<RoadmapResponse>("/api/roadmap", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  mentor: (payload: { message: string; sources?: "auto" | string[]; profile_context?: Record<string, unknown> }) =>
    requestJson<MentorChatResponse>("/api/mentor/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
