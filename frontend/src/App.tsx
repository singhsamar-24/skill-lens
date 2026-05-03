import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { Landing } from "./pages/Landing";
import { SkeletonBlock } from "./components/ui";
import { AnalysisProvider } from "./state/analysis-store";

const Dashboard = lazy(() => import("./pages/Dashboard").then((module) => ({ default: module.Dashboard })));
const Compare = lazy(() => import("./pages/Compare").then((module) => ({ default: module.Compare })));
const Roadmap = lazy(() => import("./pages/Roadmap").then((module) => ({ default: module.Roadmap })));
const Mentor = lazy(() => import("./pages/Mentor").then((module) => ({ default: module.Mentor })));
const Insights = lazy(() => import("./pages/Insights").then((module) => ({ default: module.Insights })));

function RouteFallback() {
  return (
    <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-4">
        <SkeletonBlock className="h-32" />
        <SkeletonBlock className="h-64" />
      </div>
    </main>
  );
}

export default function App() {
  return (
    <AnalysisProvider>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<Landing />} />
          <Route
            path="dashboard"
            element={
              <Suspense fallback={<RouteFallback />}>
                <Dashboard />
              </Suspense>
            }
          />
          <Route
            path="compare"
            element={
              <Suspense fallback={<RouteFallback />}>
                <Compare />
              </Suspense>
            }
          />
          <Route
            path="roadmap"
            element={
              <Suspense fallback={<RouteFallback />}>
                <Roadmap />
              </Suspense>
            }
          />
          <Route
            path="mentor"
            element={
              <Suspense fallback={<RouteFallback />}>
                <Mentor />
              </Suspense>
            }
          />
          <Route
            path="insights"
            element={
              <Suspense fallback={<RouteFallback />}>
                <Insights />
              </Suspense>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </AnalysisProvider>
  );
}
