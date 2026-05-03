import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Panel } from "../components/ui";
import { Hero } from "../components/Hero";
import { AnalysisForm } from "../components/AnalysisForm";
import { useAuth } from "../state/auth-store";
import { Link } from "react-router-dom";

export function Landing() {
  const { isAuthenticated } = useAuth();

  const stats = [
    { label: "Knowledge Base", value: "3", detail: "Specialized RAG datasets" },
    { label: "Commit Depth", value: "30", detail: "Analyzed per repository" },
    { label: "Smart Scan", value: "12", detail: "Max repositories processed" },
  ];

  return (
    <div className="w-full bg-[#FDFDFE]">
      <Hero />
      
      <section id="verification-station" className="container mx-auto px-4 py-32 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center mb-16">
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-5xl font-black tracking-tighter text-ink sm:text-6xl"
          >
            Verify Expertise.
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="mt-6 text-xl font-medium tracking-tight text-slate-500"
          >
            Connect your GitHub and upload your resume. <br className="hidden sm:block"/> We handle the complex analysis.
          </motion.p>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="mx-auto max-w-4xl"
        >
          <div className="rounded-[3rem] border border-slate-200/60 bg-white/40 p-2 shadow-[0_40px_80px_-20px_rgba(0,0,0,0.05)] backdrop-blur-2xl">
             <div className="rounded-[2.8rem] bg-white p-6 sm:p-10">
                <AnalysisForm />
             </div>
          </div>
        </motion.div>
      </section>

      <section className="container mx-auto px-4 py-32 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-3">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              <Panel className="relative overflow-hidden group hover:border-slate-300 transition-colors h-full text-center p-12 rounded-[2.5rem]">
                <p className="text-7xl font-black tracking-tighter text-ink">{stat.value}</p>
                <p className="mt-6 text-[10px] font-bold tracking-[0.2em] uppercase text-ink">{stat.label}</p>
                <p className="mt-3 text-sm font-medium text-slate-500">{stat.detail}</p>
              </Panel>
            </motion.div>
          ))}
        </div>
      </section>

      <BottomSection />
    </div>
  );
}

function BottomSection() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;

    let W = 0;
    let H = 0;
    let mx = 0;
    let my = 0;
    let targetMx = 0;
    let targetMy = 0;
    let rafId = 0;

    const resize = () => {
      const parent = canvas.parentElement;
      const width = parent ? parent.clientWidth : window.innerWidth;
      const height = parent ? parent.clientHeight : window.innerHeight;
      W = canvas.width = width;
      H = canvas.height = height;
    };

    const handleMouseMove = (event: MouseEvent) => {
      targetMx = event.clientX;
      targetMy = event.clientY;
    };

    resize();
    window.addEventListener("resize", resize);
    document.addEventListener("mousemove", handleMouseMove);

    // ISO: x -> right-down, y -> left-down, z -> up
    const iso = (x: number, y: number, z: number, ox: number, oy: number, parallax: number) => {
      const px = (mx - W / 2) / W * parallax;
      const py = (my - H / 2) / H * parallax;
      return {
        sx: ox + (x - y) * Math.cos(Math.PI / 6) + px,
        sy: oy + (x + y) * Math.sin(Math.PI / 6) - z + py,
      };
    };

    const drawFace = (
      pts: Array<{ sx: number; sy: number }>,
      fillColor: string | null,
      strokeColor: string,
      lineW = 0.8,
    ) => {
      ctx.beginPath();
      ctx.moveTo(pts[0].sx, pts[0].sy);
      for (let i = 1; i < pts.length; i += 1) ctx.lineTo(pts[i].sx, pts[i].sy);
      ctx.closePath();
      if (fillColor) {
        ctx.fillStyle = fillColor;
        ctx.fill();
      }
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = lineW;
      ctx.stroke();
    };

    const drawCube = (
      cx: number,
      cy: number,
      cz: number,
      s: number,
      ox: number,
      oy: number,
      alpha: number,
      accentColor: string | null,
      parallax = 0,
    ) => {
      const stroke = `rgba(255,255,255,${0.32 * alpha})`;
      const topFill = `rgba(255,255,255,${0.035 * alpha})`;
      const leftFill = `rgba(255,255,255,${0.02 * alpha})`;
      const rightFill = `rgba(255,255,255,${0.015 * alpha})`;
      const makeAccent = (color: string) => color.replace("1)", `${0.85 * alpha})`);

      const c = (dx: number, dy: number, dz: number) => iso(cx + dx, cy + dy, cz + dz, ox, oy, parallax);
      const p000 = c(0, 0, 0);
      const p100 = c(s, 0, 0);
      const p010 = c(0, s, 0);
      const p110 = c(s, s, 0);
      const p001 = c(0, 0, s);
      const p101 = c(s, 0, s);
      const p011 = c(0, s, s);
      const p111 = c(s, s, s);

      drawFace([p001, p101, p111, p011], topFill, stroke);
      drawFace([p000, p001, p011, p010], leftFill, stroke);
      drawFace([p100, p101, p001, p000], rightFill, stroke);

      if (accentColor) {
        const mid = p001;
        const arm = s * 0.28;
        ctx.save();
        ctx.globalAlpha = 0.9 * alpha;
        ctx.strokeStyle = makeAccent(accentColor);
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(mid.sx, mid.sy);
        ctx.lineTo(mid.sx, mid.sy - arm * 1.1);
        ctx.moveTo(mid.sx, mid.sy - arm * 0.4);
        ctx.lineTo(mid.sx - arm * 0.8, mid.sy - arm * 0.9);
        ctx.moveTo(mid.sx, mid.sy - arm * 0.4);
        ctx.lineTo(mid.sx + arm * 0.8, mid.sy - arm * 0.9);
        ctx.stroke();
        ctx.fillStyle = makeAccent(accentColor);
        ctx.beginPath();
        ctx.moveTo(mid.sx, mid.sy - arm * 1.7);
        ctx.lineTo(mid.sx + 4, mid.sy - arm * 1.7 + 4);
        ctx.lineTo(mid.sx, mid.sy - arm * 1.7 + 8);
        ctx.lineTo(mid.sx - 4, mid.sy - arm * 1.7 + 4);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }
    };

    class EdgeParticle {
      cube: IsoCube;
      t: number;
      speed: number;
      edge: number;
      color: string;
      size: number;
      trail: Array<{ x: number; y: number; z: number }>;
      trailLen: number;

      constructor(cube: IsoCube) {
        this.cube = cube;
        this.t = Math.random();
        this.speed = 0.003 + Math.random() * 0.005;
        this.edge = Math.floor(Math.random() * 12);
        this.color = Math.random() > 0.5 ? "#aaff00" : "#00c8ff";
        this.size = 2 + Math.random() * 2;
        this.trail = [];
        this.trailLen = 8;
      }

      edgePoint(t: number) {
        const c = this.cube;
        const s = c.size;
        const cx = c.x;
        const cy = c.y;
        const cz = c.z + c.dz;
        const edges = [
          [{ x: cx, y: cy, z: cz }, { x: cx + s, y: cy, z: cz }],
          [{ x: cx + s, y: cy, z: cz }, { x: cx + s, y: cy + s, z: cz }],
          [{ x: cx + s, y: cy + s, z: cz }, { x: cx, y: cy + s, z: cz }],
          [{ x: cx, y: cy + s, z: cz }, { x: cx, y: cy, z: cz }],
          [{ x: cx, y: cy, z: cz + s }, { x: cx + s, y: cy, z: cz + s }],
          [{ x: cx + s, y: cy, z: cz + s }, { x: cx + s, y: cy + s, z: cz + s }],
          [{ x: cx + s, y: cy + s, z: cz + s }, { x: cx, y: cy + s, z: cz + s }],
          [{ x: cx, y: cy + s, z: cz + s }, { x: cx, y: cy, z: cz + s }],
          [{ x: cx, y: cy, z: cz }, { x: cx, y: cy, z: cz + s }],
          [{ x: cx + s, y: cy, z: cz }, { x: cx + s, y: cy, z: cz + s }],
          [{ x: cx + s, y: cy + s, z: cz }, { x: cx + s, y: cy + s, z: cz + s }],
          [{ x: cx, y: cy + s, z: cz }, { x: cx, y: cy + s, z: cz + s }],
        ];
        const e = edges[this.edge % 12];
        return {
          x: e[0].x + (e[1].x - e[0].x) * t,
          y: e[0].y + (e[1].y - e[0].y) * t,
          z: e[0].z + (e[1].z - e[0].z) * t,
        };
      }

      update() {
        this.t += this.speed;
        if (this.t >= 1) {
          this.t = 0;
          this.edge = (this.edge + 1) % 12;
        }
        const pos = this.edgePoint(this.t);
        this.trail.push({ ...pos });
        if (this.trail.length > this.trailLen) this.trail.shift();
      }

      draw(ox: number, oy: number, parallax: number) {
        if (this.trail.length < 2) return;
        ctx.save();
        for (let i = 1; i < this.trail.length; i += 1) {
          const a = i / this.trail.length;
          const p0 = iso(this.trail[i - 1].x, this.trail[i - 1].y, this.trail[i - 1].z, ox, oy, parallax);
          const p1 = iso(this.trail[i].x, this.trail[i].y, this.trail[i].z, ox, oy, parallax);
          ctx.beginPath();
          ctx.moveTo(p0.sx, p0.sy);
          ctx.lineTo(p1.sx, p1.sy);
          ctx.strokeStyle = this.color;
          ctx.globalAlpha = a * 0.9 * this.cube.alpha;
          ctx.lineWidth = this.size * a;
          ctx.stroke();
        }
        const head = this.trail[this.trail.length - 1];
        const hp = iso(head.x, head.y, head.z, ox, oy, parallax);
        const grd = ctx.createRadialGradient(hp.sx, hp.sy, 0, hp.sx, hp.sy, this.size * 3);
        grd.addColorStop(0, this.color);
        grd.addColorStop(1, "transparent");
        ctx.globalAlpha = this.cube.alpha;
        ctx.fillStyle = grd;
        ctx.beginPath();
        ctx.arc(hp.sx, hp.sy, this.size * 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    class IsoCube {
      x: number;
      y: number;
      z: number;
      bx: number;
      by: number;
      bz: number;
      size: number;
      hasAccent: boolean;
      accentColor: string | null;
      vx: number;
      vy: number;
      vz: number;
      ax: number;
      ay: number;
      az: number;
      phase: number;
      floatSpeed: number;
      floatAmp: number;
      rotOff: number;
      parallax: number;
      alpha: number;
      dz: number;
      particles: EdgeParticle[];

      constructor(x: number, y: number, z: number, size: number, hasAccent: boolean) {
        this.x = x;
        this.y = y;
        this.z = z;
        this.bx = x;
        this.by = y;
        this.bz = z;
        this.size = size;
        this.hasAccent = hasAccent;
        this.accentColor = hasAccent
          ? (Math.random() > 0.5 ? "rgba(170,255,0,1)" : "rgba(0,200,255,1)")
          : null;
        this.vx = (Math.random() - 0.5) * 0.004;
        this.vy = (Math.random() - 0.5) * 0.004;
        this.vz = (Math.random() - 0.5) * 0.003;
        this.ax = 0;
        this.ay = 0;
        this.az = 0;
        this.phase = Math.random() * Math.PI * 2;
        this.floatSpeed = 0.3 + Math.random() * 0.5;
        this.floatAmp = 6 + Math.random() * 10;
        this.rotOff = Math.random() * 20;
        this.parallax = 15 + Math.random() * 30;
        this.alpha = 0.4 + Math.random() * 0.6;
        this.dz = 0;
        this.particles = [];
        if (Math.random() > 0.4) {
          for (let i = 0; i < 3; i += 1) this.particles.push(new EdgeParticle(this));
        }
      }

      update(t: number) {
        this.ax = (this.bx - this.x) * 0.02 + this.vx * -0.04;
        this.ay = (this.by - this.y) * 0.02 + this.vy * -0.04;
        this.az = (this.bz - this.z) * 0.02 + this.vz * -0.04;
        this.vx += this.ax;
        this.vy += this.ay;
        this.vz += this.az;
        this.x += this.vx;
        this.y += this.vy;
        this.z += this.vz;
        const ft = t * this.floatSpeed + this.phase;
        this.dz = Math.sin(ft) * this.floatAmp;
        this.particles.forEach((p) => p.update());
      }

      draw(ox: number, oy: number) {
        const renderZ = this.z + this.dz;
        drawCube(this.x, this.y, renderZ, this.size, ox, oy, this.alpha, this.accentColor, this.parallax);
        this.particles.forEach((p) => p.draw(ox, oy, this.parallax));
      }

      depth() {
        return this.x + this.y - this.z;
      }
    }

    class Beam {
      a: IsoCube;
      b: IsoCube;
      t: number;
      speed: number;
      color: string;
      trail: Array<{ x: number; y: number }>;
      active: boolean;

      constructor(a: IsoCube, b: IsoCube) {
        this.a = a;
        this.b = b;
        this.t = 0;
        this.speed = 0.006 + Math.random() * 0.008;
        this.color = Math.random() > 0.5 ? "rgba(170,255,0," : "rgba(0,200,255,";
        this.trail = [];
        this.active = true;
      }

      update() {
        this.t += this.speed;
        if (this.t > 1.2) this.active = false;
        const s = this.a.size / 2;
        const ox = W * 0.62;
        const oy = H * 0.5;
        const pa = iso(this.a.x + s, this.a.y + s, this.a.z + this.a.dz + s, ox, oy, 20);
        const pb = iso(this.b.x + s, this.b.y + s, this.b.z + this.b.dz + s, ox, oy, 20);
        const t = Math.min(this.t, 1);
        this.trail.push({ x: pa.sx + (pb.sx - pa.sx) * t, y: pa.sy + (pb.sy - pa.sy) * t });
        if (this.trail.length > 30) this.trail.shift();
      }

      draw() {
        if (this.trail.length < 2) return;
        ctx.save();
        for (let i = 1; i < this.trail.length; i += 1) {
          const a = (i / this.trail.length) * Math.min(this.t * 2, 1) * (this.t > 1 ? Math.max(0, 1 - (this.t - 1) * 3) : 1);
          ctx.beginPath();
          ctx.moveTo(this.trail[i - 1].x, this.trail[i - 1].y);
          ctx.lineTo(this.trail[i].x, this.trail[i].y);
          ctx.strokeStyle = `${this.color}${a * 0.6})`;
          ctx.lineWidth = 1.5 * (i / this.trail.length);
          ctx.stroke();
        }
        ctx.restore();
      }
    }

    class DataChip {
      x = 0;
      y = 0;
      vy = 0;
      vx = 0;
      alpha = 0;
      fadeIn = 0;
      life = 0;
      maxLife = 0;
      labels = [
        "React.js - 91%",
        "MLOps - 34%",
        "System Design - 68%",
        "Trust Score: 87",
        "Gap: -14pts",
        "NLP - 72%",
        "FastAPI - 88%",
        "FAISS - 61%",
      ];
      label = "";
      color = "";
      w = 0;
      h = 0;

      constructor() {
        this.reset();
      }

      reset() {
        this.x = W * 0.5 + Math.random() * W * 0.45;
        this.y = Math.random() * H;
        this.vy = -0.15 - Math.random() * 0.2;
        this.vx = (Math.random() - 0.5) * 0.1;
        this.alpha = 0;
        this.fadeIn = 0.01 + Math.random() * 0.02;
        this.life = 0;
        this.maxLife = 200 + Math.random() * 300;
        this.label = this.labels[Math.floor(Math.random() * this.labels.length)];
        this.color = Math.random() > 0.5 ? "#aaff00" : "#00c8ff";
        this.w = this.label.length * 6.5 + 20;
        this.h = 20;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life += 1;
        if (this.life < 30) this.alpha = Math.min(1, this.alpha + this.fadeIn);
        if (this.life > this.maxLife - 40) this.alpha = Math.max(0, this.alpha - 0.02);
        if (this.life > this.maxLife || this.y < -40) this.reset();
      }

      draw() {
        ctx.save();
        ctx.globalAlpha = this.alpha * 0.7;
        ctx.fillStyle = "rgba(8,8,8,0.8)";
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 0.7;
        ctx.beginPath();
        ctx.roundRect(this.x - this.w / 2, this.y - this.h / 2, this.w, this.h, 2);
        ctx.fill();
        ctx.stroke();
        ctx.font = "10px DM Mono, monospace";
        ctx.fillStyle = this.color;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(this.label, this.x, this.y);
        ctx.restore();
      }
    }

    const cubes: IsoCube[] = [];
    const configs: Array<[number, number, number, number, boolean]> = [
      [0, 0, 0, 90, true],
      [100, -20, 30, 70, false],
      [-80, 80, 20, 60, true],
      [120, 80, 0, 75, false],
      [-30, -90, 10, 55, true],
      [200, 10, 40, 55, false],
      [-110, -30, 0, 45, false],
      [60, 140, 20, 50, true],
      [220, 100, 10, 60, false],
      [-60, 160, 30, 40, false],
      [310, -20, 0, 50, false],
      [150, -80, 40, 45, true],
    ];
    configs.forEach(([x, y, z, s, acc]) => cubes.push(new IsoCube(x, y, z, s, acc)));

    let beams: Beam[] = [];
    const chips = Array.from({ length: 8 }, () => new DataChip());
    let beamTimer = 0;
    let t = 0;

    const loop = () => {
      rafId = window.requestAnimationFrame(loop);
      t += 0.016;

      mx += (targetMx - mx) * 0.08;
      my += (targetMy - my) * 0.08;

      ctx.clearRect(0, 0, W, H);

      const ox = W * 0.62;
      const oy = H * 0.5;

      cubes.forEach((c) => c.update(t));
      cubes.sort((a, b) => a.depth() - b.depth());
      cubes.forEach((c) => c.draw(ox, oy));

      beamTimer += 1;
      if (beamTimer > 30) {
        beamTimer = 0;
        const a = cubes[Math.floor(Math.random() * cubes.length)];
        let b = cubes[Math.floor(Math.random() * cubes.length)];
        if (a === b) b = cubes[(cubes.indexOf(a) + 1) % cubes.length];
        beams.push(new Beam(a, b));
      }

      beams.forEach((b) => b.update());
      beams.forEach((b) => b.draw());
      beams = beams.filter((b) => b.active);

      chips.forEach((chip) => {
        chip.update();
        chip.draw();
      });
    };

    loop();

    return () => {
      window.removeEventListener("resize", resize);
      document.removeEventListener("mousemove", handleMouseMove);
      window.cancelAnimationFrame(rafId);
    };
  }, []);

  return (
    <section className="bottom-section relative min-h-screen overflow-hidden bg-[#080808] text-white">
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400&display=swap');
.bottom-section__eyebrow{
  font-family:'Syne',sans-serif;
  font-size:0.7rem;letter-spacing:0.18em;text-transform:uppercase;
  color:#aaff00;margin-bottom:1.6rem;display:flex;align-items:center;gap:0.6rem;
  opacity:0;animation:bottomSectionUp 0.8s 0.1s cubic-bezier(0.16,1,0.3,1) forwards;
}
.bottom-section__eyebrow::before{content:'';width:22px;height:1px;background:#aaff00}
.bottom-section__title{
  font-family:'Syne',sans-serif;font-weight:800;
  font-size:clamp(2.8rem,5.5vw,5rem);
  line-height:1.04;letter-spacing:-0.03em;color:#fff;margin-bottom:2rem;
  opacity:0;animation:bottomSectionUp 0.9s 0.25s cubic-bezier(0.16,1,0.3,1) forwards;
}
.bottom-section__copy{
  font-size:clamp(0.85rem,1.1vw,1rem);line-height:1.8;color:rgba(255,255,255,0.5);
  max-width:480px;margin-bottom:2.8rem;opacity:0;
  animation:bottomSectionUp 0.9s 0.4s cubic-bezier(0.16,1,0.3,1) forwards;
}
.bottom-section__cta{
  display:flex;gap:1.2rem;align-items:center;opacity:0;
  animation:bottomSectionUp 0.9s 0.55s cubic-bezier(0.16,1,0.3,1) forwards;
}
.bottom-section__btn{
  font-family:'Syne',sans-serif;font-weight:700;font-size:0.78rem;letter-spacing:0.07em;text-transform:uppercase;
  padding:0.8rem 2rem;border-radius:2px;cursor:pointer;border:none;transition:transform 0.2s, box-shadow 0.2s;
}
.bottom-section__btn--primary{background:#aaff00;color:#080808}
.bottom-section__btn--primary:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(170,255,0,0.35)}
.bottom-section__btn--ghost{background:none;border:1px solid rgba(255,255,255,0.15);color:rgba(255,255,255,0.6)}
.bottom-section__btn--ghost:hover{border-color:rgba(255,255,255,0.4);color:#fff}
@keyframes bottomSectionUp{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:none}}
@media (max-width: 900px){
  .bottom-section__content{max-width:100%;}
}
`}
      </style>
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" />
      <div className="relative z-10 flex min-h-screen items-center px-[6vw]">
        <div className="bottom-section__content max-w-[52vw]">
          <div className="bottom-section__eyebrow">AI Skill Intelligence</div>
          <h2 className="bottom-section__title">
            Bridging Talent
            <br />
            &amp; Industry.
          </h2>
          <p className="bottom-section__copy">
            SkillLens uses autonomous AI to extract proof-based skills from your actual work - verified through code,
            projects, and history. Not just listed. {" "}
            <strong className="text-white/80">Proven.</strong>
          </p>
          <div className="bottom-section__cta pointer-events-auto">
            <button type="button" className="bottom-section__btn bottom-section__btn--primary">Analyze My Skills</button>
            <button type="button" className="bottom-section__btn bottom-section__btn--ghost">See How It Works -&gt;</button>
          </div>
        </div>
      </div>
    </section>
  );
}
