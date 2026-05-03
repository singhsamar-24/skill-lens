import { motion } from "framer-motion";
import { Github, Mail } from "lucide-react";
import { useAuth } from "../state/auth-store";
import { Page, Button } from "../components/ui";
import { Scene3D } from "../components/Scene3D";
import { Suspense } from "react";
import { Navigate } from "react-router-dom";

export function Login() {
  const { login, loginWithProvider, isAuthenticated, loading } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <Page className="relative flex min-h-[calc(100svh-5rem)] flex-col items-center justify-center overflow-hidden">
      <Suspense fallback={null}>
        <Scene3D />
      </Suspense>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-md px-4"
      >
        <div className="rounded-[3rem] border border-slate-200/60 bg-white/40 p-2 shadow-[0_40px_80px_-20px_rgba(0,0,0,0.05)] backdrop-blur-2xl">
          <div className="rounded-[2.8rem] bg-white p-10 text-center">
            <div className="mb-8 flex justify-center">
              <div className="grid h-16 w-16 place-items-center rounded-3xl bg-ink text-white shadow-2xl">
                <Github size={32} />
              </div>
            </div>
            
            <h1 className="text-3xl font-black tracking-tighter text-ink sm:text-4xl">
              Welcome back.
            </h1>
            <p className="mt-4 text-base font-medium text-slate-500">
              Sign in with your GitHub account to continue your verification journey.
            </p>

            <div className="mt-10">
              <div className="grid gap-3">
              <Button
                onClick={login}
                disabled={loading}
                className="h-16 w-full rounded-2xl bg-ink text-base font-bold tracking-wide text-white shadow-2xl transition-all hover:bg-slate-800 disabled:opacity-50"
              >
                {loading ? (
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-white/20 border-t-white" />
                ) : (
                  <span className="flex items-center gap-3">
                    <Github size={20} />
                    Continue with GitHub
                  </span>
                )}
              </Button>

              <Button
                onClick={() => loginWithProvider("google")}
                disabled={loading}
                variant="secondary"
                className="h-16 w-full rounded-2xl text-base font-bold tracking-wide transition-all disabled:opacity-50"
              >
                <span className="flex items-center gap-3">
                  <Mail size={20} />
                  Continue with Google
                </span>
              </Button>
              </div>
            </div>

            <p className="mt-8 text-[10px] font-bold uppercase tracking-widest text-muted/60">
              SkillLens Verification Platform
            </p>
          </div>
        </div>
      </motion.div>
    </Page>
  );
}
