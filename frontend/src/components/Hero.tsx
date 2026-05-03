import { motion } from "framer-motion";
import { ArrowDown } from "lucide-react";
import { Suspense } from "react";
import { Scene3D } from "./Scene3D";

export function Hero() {
  const scrollToForm = () => {
    const element = document.getElementById("verification-station");
    if (element) {
      const offset = 100; // Account for sticky header
      const bodyRect = document.body.getBoundingClientRect().top;
      const elementRect = element.getBoundingClientRect().top;
      const elementPosition = elementRect - bodyRect;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth"
      });
    }
  };

  return (
    <section className="relative flex min-h-[100svh] flex-col items-center justify-center overflow-hidden bg-transparent">
      {/* 3D Immersive Background */}
      <Suspense fallback={<div className="absolute inset-0 bg-[#FDFDFE]" />}>
        <Scene3D />
      </Suspense>

      <div className="container relative z-10 mx-auto px-4 text-center sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
          className="mx-auto max-w-5xl"
        >
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="mb-8 inline-flex items-center rounded-full border border-slate-200/50 bg-white/40 px-5 py-2 text-[10px] font-bold uppercase tracking-[0.3em] text-ink backdrop-blur-xl shadow-sm"
          >
            SkillLens Intelligence
          </motion.div>

          <h1 className="text-balance text-7xl font-black tracking-tighter text-ink sm:text-8xl lg:text-[10rem] leading-[0.9]">
            Evidence <br /> 
            <span className="bg-gradient-to-br from-slate-400 to-slate-800 bg-clip-text text-transparent">
              Over Claims.
            </span>
          </h1>

          <p className="mx-auto mt-10 max-w-2xl text-balance text-lg font-medium leading-relaxed text-slate-500 sm:text-xl tracking-tight">
            A new standard for professional verification. We analyze your actual code contributions to build an undeniable, evidence-backed career profile.
          </p>

          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.8 }}
            className="mt-16 flex justify-center"
          >
            <button 
              onClick={scrollToForm}
              className="group flex h-14 items-center gap-3 rounded-full bg-ink px-8 text-[13px] font-bold uppercase tracking-widest text-white transition-all duration-500 hover:scale-105 hover:bg-slate-800 hover:shadow-2xl"
            >
              Initialize Scan
              <ArrowDown size={16} className="transition-transform duration-500 group-hover:translate-y-1" />
            </button>
          </motion.div>
        </motion.div>
      </div>

      {/* Elegant fade out to blend with next section */}
      <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-[#FDFDFE] to-transparent" />
    </section>
  );
}
