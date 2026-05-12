"use client";

import { motion } from 'framer-motion';
import { ArrowRight, FileCheck, BarChart3, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { authService } from './services/mockServices';

export default function Landing() {
  const router = useRouter();

  useEffect(() => {
    if (authService.isAuthenticated()) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-2"
        >
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-xl">P</span>
          </div>
          <span className="text-2xl font-bold text-secondary">
            Porfio
          </span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex gap-3"
        >
          <button
            onClick={() => router.push('/lofi')}
            className="px-4 py-2 text-sm bg-card text-card-foreground rounded-lg hover:bg-muted transition-colors border border-border shadow-sm"
          >
            View Lo-Fi
          </button>
          <button
            onClick={() => router.push('/login')}
            className="px-6 py-2 rounded-lg hover:bg-muted transition-colors font-medium"
          >
            Masuk
          </button>
          <button
            onClick={() => router.push('/register')}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-medium shadow-sm"
          >
            Daftar Gratis
          </button>
        </motion.div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-card rounded-full mb-6 border border-border shadow-sm">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-card-foreground">Powered by AI Analysis</span>
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-6xl font-bold mb-6 leading-tight text-foreground"
          >
            Temukan Karir Impian dengan{' '}
            <span className="text-primary">
              Analisis CV
            </span>{' '}
            Cerdas
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-xl text-foreground/80 mb-10 max-w-2xl mx-auto"
          >
            Upload CV Anda dan dapatkan analisis mendalam, scoring profesional, dan rekomendasi
            pekerjaan yang cocok dengan keahlian Anda
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex gap-4 justify-center"
          >
            <button
              onClick={() => router.push('/register')}
              className="px-8 py-4 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-all flex items-center gap-2 group shadow-sm font-medium"
            >
              Mulai Sekarang
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="px-8 py-4 bg-card text-card-foreground border border-border rounded-xl hover:bg-muted transition-colors font-medium shadow-sm">
              Lihat Demo
            </button>
          </motion.div>
        </div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid md:grid-cols-3 gap-8 mt-32"
        >
          <div className="bg-card text-card-foreground rounded-2xl p-8 border border-border shadow-sm hover:shadow-md transition-shadow">
            <div className="w-14 h-14 bg-secondary rounded-xl flex items-center justify-center mb-4">
              <FileCheck className="w-7 h-7 text-secondary-foreground" />
            </div>
            <h3 className="text-xl font-bold mb-3">Upload CV Mudah</h3>
            <p className="text-foreground/70">
              Upload CV dalam format PDF, DOCX, atau gambar. Sistem kami akan memproses dengan
              cepat dan akurat.
            </p>
          </div>

          <div className="bg-card text-card-foreground rounded-2xl p-8 border border-border shadow-sm hover:shadow-md transition-shadow">
            <div className="w-14 h-14 bg-primary rounded-xl flex items-center justify-center mb-4">
              <BarChart3 className="w-7 h-7 text-primary-foreground" />
            </div>
            <h3 className="text-xl font-bold mb-3">Analisis Mendalam</h3>
            <p className="text-foreground/70">
              Dapatkan scoring profesional dari skills, pengalaman, dan potensi karir Anda dengan
              AI terbaru.
            </p>
          </div>

          <div className="bg-card text-card-foreground rounded-2xl p-8 border border-border shadow-sm hover:shadow-md transition-shadow">
            <div className="w-14 h-14 bg-secondary rounded-xl flex items-center justify-center mb-4">
              <Sparkles className="w-7 h-7 text-secondary-foreground" />
            </div>
            <h3 className="text-xl font-bold mb-3">Rekomendasi Personal</h3>
            <p className="text-foreground/70">
              Temukan pekerjaan yang paling cocok dengan profil Anda, lengkap dengan estimasi gaji
              dan tips.
            </p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}