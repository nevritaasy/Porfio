"use client";

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Loader2,
  TrendingUp,
  Briefcase,
  MapPin,
  DollarSign,
  CheckCircle2,
  Star,
  Award,
  Target,
  AlertCircle,
} from 'lucide-react';
import { authService, cvService } from '../services/mockServices';

export default function Analysis() {
  const router = useRouter();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [user, setUser] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [analysis, setAnalysis] = useState<any>(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      router.push('/login');
      return;
    }
    setUser(currentUser);

    // Jalankan simulasi analisis AI
    cvService.analyzeCV().then((result: any) => {
      setAnalysis(result);
      setIsAnalyzing(false);
    });
  }, [router]);

  if (!user) return null;

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="p-2 hover:bg-muted rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-muted-foreground" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-sm">
                <span className="text-primary-foreground font-bold text-xl">P</span>
              </div>
              <span className="text-2xl font-bold text-secondary">
                Porfio
              </span>
            </div>
          </div>
          <div className="text-right hidden sm:block">
            <p className="font-medium">{user.name}</p>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {isAnalyzing ? (
          /* --- LOADING STATE --- */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-2xl mx-auto text-center py-20"
          >
            <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-8">
              <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
            <h2 className="text-3xl font-bold mb-4">Menganalisis CV Anda...</h2>
            <p className="text-xl text-muted-foreground mb-8">
              AI kami sedang membedah keahlian Anda untuk mencari peluang karir terbaik.
            </p>
            <div className="space-y-3 max-w-md mx-auto text-left">
              {[
                'Membaca konten CV...',
                'Mengidentifikasi keahlian teknis...',
                'Menghitung scoring profesional...',
                'Mencocokkan dengan database pekerjaan...',
              ].map((text, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.8 }}
                  className="flex items-center gap-3 bg-card border border-border rounded-xl p-4 shadow-sm"
                >
                  <CheckCircle2 className="w-5 h-5 text-secondary" />
                  <span className="text-sm font-medium">{text}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        ) : (
          /* --- RESULTS STATE --- */
          <div className="space-y-8">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-4xl font-bold mb-3">Hasil Analisis CV</h1>
              <p className="text-xl text-muted-foreground">
                Berdasarkan data yang diupload, berikut adalah profil profesional Anda.
              </p>
            </motion.div>

            {/* Overall Score Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-secondary rounded-3xl p-8 text-secondary-foreground shadow-md border border-secondary"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Award className="w-6 h-6 text-primary" />
                    <span className="text-lg opacity-90">Skor Keseluruhan</span>
                  </div>
                  <div className="flex items-baseline gap-3">
                    <span className="text-7xl font-bold">{analysis.overallScore}</span>
                    <span className="text-3xl opacity-70">/100</span>
                  </div>
                  <p className="mt-4 text-secondary-foreground/80 max-w-md">
                    Luar biasa! Profil CV Anda menunjukkan spesialisasi yang sangat kuat di bidang teknologi modern.
                  </p>
                </div>
                <div className="hidden md:block">
                  <div className="w-40 h-40 relative">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle
                        cx="80" cy="80" r="70"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="12" fill="none"
                      />
                      <motion.circle
                        cx="80" cy="80" r="70"
                        stroke="#DB924C" /* Warna Primary */
                        strokeWidth="12" fill="none"
                        strokeLinecap="round"
                        initial={{ strokeDasharray: '439.6', strokeDashoffset: '439.6' }}
                        animate={{
                          strokeDashoffset: 439.6 - (439.6 * analysis.overallScore) / 100,
                        }}
                        transition={{ duration: 1.5, ease: 'easeOut' }}
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </motion.div>

            <div className="grid lg:grid-cols-3 gap-8">
              {/* Skills Breakdown - 1 Column */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-card rounded-3xl p-8 border border-border shadow-sm lg:col-span-1"
              >
                <div className="flex items-center gap-2 mb-6">
                  <Star className="w-6 h-6 text-primary" />
                  <h2 className="text-2xl font-bold">Keahlian</h2>
                </div>
                <div className="space-y-6">
                  {analysis.skills.map((skill: any, index: number) => (
                    <div key={index}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-foreground">{skill.name}</span>
                        <span className="text-sm font-bold text-primary">{skill.level}%</span>
                      </div>
                      <div className="h-2.5 bg-muted rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${skill.level}%` }}
                          transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                          className="h-full bg-primary rounded-full"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* Job Recommendations - 2 Columns */}
              <div className="lg:col-span-2 space-y-6">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-6 h-6 text-secondary" />
                  <h2 className="text-2xl font-bold">Rekomendasi Karir</h2>
                </div>
                {analysis.recommendations.map((job: any, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className="bg-card rounded-2xl p-6 border border-border shadow-sm hover:border-primary/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1 text-left">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="text-xl font-bold text-foreground">{job.role}</h3>
                          <span className="bg-secondary/10 text-secondary text-xs font-bold px-2 py-1 rounded-md border border-secondary/20">
                            {job.matchScore}% MATCH
                          </span>
                        </div>
                        <p className="text-muted-foreground mb-3">{job.company}</p>
                        <div className="flex flex-wrap gap-4 text-sm font-medium text-foreground/70">
                          <div className="flex items-center gap-1.5">
                            <MapPin className="size-4 text-primary" /> {job.location}
                          </div>
                          <div className="flex items-center gap-1.5">
                            <DollarSign className="size-4 text-primary" /> {job.salary}
                          </div>
                        </div>
                      </div>
                      <div className="w-14 h-14 bg-muted rounded-xl flex items-center justify-center">
                        <Briefcase className="size-7 text-secondary" />
                      </div>
                    </div>
                    <div className="bg-muted/50 rounded-xl p-4 mb-4">
                      <p className="text-xs font-bold text-secondary uppercase tracking-wider mb-2">Analisis AI:</p>
                      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {job.reasons.map((reason: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-2 text-sm text-foreground/80">
                            <CheckCircle2 className="size-4 text-primary mt-0.5" />
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <button className="w-full py-2.5 bg-primary text-primary-foreground rounded-lg font-bold hover:opacity-90 shadow-sm transition-opacity">
                      Lamar Sekarang
                    </button>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid md:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 }}
                className="bg-card rounded-2xl p-6 border border-border"
              >
                <div className="flex items-center gap-2 mb-4 text-secondary">
                  <Award className="size-5" />
                  <h3 className="font-bold">Kekuatan Utama</h3>
                </div>
                <ul className="space-y-3">
                  {analysis.strengths.map((str: string, i: number) => (
                    <li key={i} className="flex gap-3 text-sm text-foreground/80 text-left">
                      <span className="size-1.5 bg-primary rounded-full mt-2 shrink-0" />
                      {str}
                    </li>
                  ))}
                </ul>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7 }}
                className="bg-card rounded-2xl p-6 border border-border"
              >
                <div className="flex items-center gap-2 mb-4 text-accent">
                  <AlertCircle className="size-5" />
                  <h3 className="font-bold">Saran Pengembangan</h3>
                </div>
                <ul className="space-y-3">
                  {analysis.improvements.map((imp: string, i: number) => (
                    <li key={i} className="flex gap-3 text-sm text-foreground/80 text-left">
                      <span className="size-1.5 bg-accent rounded-full mt-2 shrink-0" />
                      {imp}
                    </li>
                  ))}
                </ul>
              </motion.div>
            </div>

            {/* Final Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8 border-t border-border">
              <button
                onClick={() => router.push('/upload-cv')}
                className="px-8 py-3 bg-card border border-border text-foreground rounded-xl font-bold hover:bg-muted transition-all"
              >
                Ganti File CV
              </button>
              <button
                onClick={() => router.push('/dashboard')}
                className="px-8 py-3 bg-secondary text-secondary-foreground rounded-xl font-bold hover:opacity-90 shadow-sm transition-all"
              >
                Selesai & Ke Dashboard
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}