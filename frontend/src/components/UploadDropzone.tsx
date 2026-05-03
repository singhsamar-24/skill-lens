import { UploadCloud, X, FileText, CheckCircle2 } from "lucide-react";
import { cx } from "../lib/format";
import { motion, AnimatePresence } from "framer-motion";

export function UploadDropzone({ file, onChange }: { file?: File; onChange: (file?: File) => void }) {
  return (
    <div className="group relative">
      <AnimatePresence mode="wait">
        {!file ? (
          <motion.label
            key="empty"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-2xl bg-slate-50 transition-all hover:bg-slate-100 hover:shadow-inner"
          >
            <input
              className="sr-only"
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => onChange(event.target.files?.[0])}
            />
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-white shadow-sm transition-transform duration-500 group-hover:scale-110">
              <UploadCloud className="text-ink transition-colors" size={24} />
            </div>
            <p className="mt-4 text-base font-bold text-ink">Select Resume Document</p>
            <p className="mt-1 text-xs font-medium text-slate-400">PDF format • Max 5MB</p>
          </motion.label>
        ) : (
          <motion.div
            key="filled"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative flex min-h-[160px] flex-col items-center justify-center rounded-2xl bg-ink p-6 text-center shadow-xl"
          >
            <div className="absolute top-4 right-4">
               <button
                type="button"
                onClick={() => onChange(undefined)}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white/60 transition-all hover:bg-rose-500 hover:text-white"
              >
                <X size={16} />
              </button>
            </div>
            
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-white/10 text-white backdrop-blur-md">
              <FileText size={24} />
            </div>
            
            <div className="mt-4 flex flex-col items-center">
              <div className="flex items-center gap-2">
                <p className="max-w-[200px] truncate text-base font-bold text-white">{file.name}</p>
                <CheckCircle2 size={16} className="text-emerald-400" />
              </div>
              <p className="mt-1 text-xs font-medium text-white/60">
                {(file.size / 1024 / 1024).toFixed(2)} MB • Ready for parsing
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
