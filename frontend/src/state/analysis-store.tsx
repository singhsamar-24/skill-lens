import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { api } from "../lib/api";
import type { CodeforcesAnalysis, CompareResponse, GitHubAnalysis, LeetCodeAnalysis, ResumeAnalysis, RoadmapResponse } from "../types";

type Status = "idle" | "loading" | "ready" | "error";

interface RunInput {
  githubUsername: string;
  leetcodeUsername?: string;
  codeforcesUsername?: string;
  targetRole: string;
  resumeFile: File;
}

interface AnalysisState {
  github?: GitHubAnalysis;
  resume?: ResumeAnalysis;
  leetcode?: LeetCodeAnalysis;
  codeforces?: CodeforcesAnalysis;
  comparison?: CompareResponse;
  roadmap?: RoadmapResponse;
  targetRole: string;
  statuses: Record<"github" | "resume" | "leetcode" | "codeforces" | "compare" | "roadmap", Status>;
  errors: string[];
  runAnalysis: (input: RunInput) => Promise<void>;
  generateRoadmap: () => Promise<void>;
  reset: () => void;
}

const initialStatuses: AnalysisState["statuses"] = {
  github: "idle",
  resume: "idle",
  leetcode: "idle",
  codeforces: "idle",
  compare: "idle",
  roadmap: "idle",
};

const AnalysisContext = createContext<AnalysisState | null>(null);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [github, setGithub] = useState<GitHubAnalysis>();
  const [resume, setResume] = useState<ResumeAnalysis>();
  const [leetcode, setLeetcode] = useState<LeetCodeAnalysis>();
  const [codeforces, setCodeforces] = useState<CodeforcesAnalysis>();
  const [comparison, setComparison] = useState<CompareResponse>();
  const [roadmap, setRoadmap] = useState<RoadmapResponse>();
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [statuses, setStatuses] = useState(initialStatuses);
  const [errors, setErrors] = useState<string[]>([]);

  const setStatus = useCallback((key: keyof AnalysisState["statuses"], value: Status) => {
    setStatuses((current) => ({ ...current, [key]: value }));
  }, []);

  const runAnalysis = useCallback(async (input: RunInput) => {
    setTargetRole(input.targetRole);
    setErrors([]);
    setComparison(undefined);
    setRoadmap(undefined);
    setLeetcode(undefined);
    setCodeforces(undefined);
    setStatuses({
      github: "loading",
      resume: "loading",
      leetcode: input.leetcodeUsername ? "loading" : "idle",
      codeforces: input.codeforcesUsername ? "loading" : "idle",
      compare: "idle",
      roadmap: "idle",
    });

    let nextGithub: GitHubAnalysis | undefined;
    let nextResume: ResumeAnalysis | undefined;
    let nextLeetcode: LeetCodeAnalysis | undefined;
    let nextCodeforces: CodeforcesAnalysis | undefined;

    const githubPromise = api
      .analyzeGitHub(input.githubUsername)
      .then((result) => {
        nextGithub = result;
        setGithub(result);
        setStatus("github", "ready");
      })
      .catch((error: Error) => {
        setStatus("github", "error");
        setErrors((current) => [...current, `GitHub: ${error.message}`]);
      });

    const resumePromise = api
      .analyzeResume(input.resumeFile)
      .then((result) => {
        nextResume = result;
        setResume(result);
        setStatus("resume", "ready");
      })
      .catch((error: Error) => {
        setStatus("resume", "error");
        setErrors((current) => [...current, `Resume: ${error.message}`]);
      });

    const leetcodePromise = input.leetcodeUsername
      ? api
          .analyzeLeetCode(input.leetcodeUsername)
          .then((result) => {
            nextLeetcode = result;
            setLeetcode(result);
            setStatus("leetcode", "ready");
          })
          .catch((error: Error) => {
            setStatus("leetcode", "error");
            setErrors((current) => [...current, `LeetCode: ${error.message}`]);
          })
      : Promise.resolve();

    const codeforcesPromise = input.codeforcesUsername
      ? api
          .analyzeCodeforces(input.codeforcesUsername)
          .then((result) => {
            nextCodeforces = result;
            setCodeforces(result);
            setStatus("codeforces", "ready");
          })
          .catch((error: Error) => {
            setStatus("codeforces", "error");
            setErrors((current) => [...current, `Codeforces: ${error.message}`]);
          })
      : Promise.resolve();

    await Promise.all([githubPromise, resumePromise, leetcodePromise, codeforcesPromise]);

    if (nextGithub && nextResume) {
      setStatus("compare", "loading");
      try {
        const result = await api.compare({
          github: nextGithub,
          resume: nextResume,
          leetcode: nextLeetcode,
          codeforces: nextCodeforces,
          target_role: input.targetRole,
        });
        setComparison(result);
        setStatus("compare", "ready");
      } catch (error) {
        setStatus("compare", "error");
        setErrors((current) => [...current, `Compare: ${(error as Error).message}`]);
      }
    }
  }, [setStatus]);

  const generateRoadmap = useCallback(async () => {
    if (!comparison) return;
    setStatus("roadmap", "loading");
    try {
      const result = await api.roadmap({ comparison, target_role: targetRole });
      setRoadmap(result);
      setStatus("roadmap", "ready");
    } catch (error) {
      setStatus("roadmap", "error");
      setErrors((current) => [...current, `Roadmap: ${(error as Error).message}`]);
    }
  }, [comparison, targetRole]);

  const reset = useCallback(() => {
    setGithub(undefined);
    setResume(undefined);
    setLeetcode(undefined);
    setCodeforces(undefined);
    setComparison(undefined);
    setRoadmap(undefined);
    setStatuses(initialStatuses);
    setErrors([]);
    setTargetRole("Software Engineer");
  }, []);

  const value = useMemo(
    () => ({ github, resume, leetcode, codeforces, comparison, roadmap, targetRole, statuses, errors, runAnalysis, generateRoadmap, reset }),
    [github, resume, leetcode, codeforces, comparison, roadmap, targetRole, statuses, errors],
  );

  return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>;
}

export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error("useAnalysis must be used inside AnalysisProvider");
  }
  return context;
}
