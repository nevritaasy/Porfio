"use client";

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Upload,
  FileText,
  BarChart3,
  LogOut,
  User,
  Calendar,
  CheckCircle2,
} from 'lucide-react';
import { authService, cvService } from '../services/mockServices';

export default function Dashboard() {
  const router = useRouter();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [user, setUser] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [cvData, setCvData] = useState<any>(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      router.push('/login');
      return;
    }
    setUser(currentUser);
    setCvData(cvService.getStoredCV());
  }, [router]);

  const handleLogout = () => {
    authService.logout();
    router.push('/');
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-sm">
              <span className="text-primary-foreground font-bold text-xl">P</span>
            </div>
            <span className="text-2xl font-bold text-secondary">
              Porfio
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="font-medium text-foreground">{user.name}</p>
              <p className="text-sm text-muted-foreground">{user.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-muted rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5 text-muted-foreground hover:text-destructive transition-colors" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold mb-2 text-foreground">
            Selamat datang kembali, {user.name}! 👋
          </h1>
          <p className="text-xl text-muted-foreground">
            Siap untuk menganalisis CV dan menemukan peluang karir terbaik?
          </p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-card backdrop-blur-sm rounded-2xl p-6 border border-border shadow-sm"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-secondary/10 rounded-xl flex items-center justify-center">
                <FileText className="w-6 h-6 text-secondary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">CV Diupload</p>
                <p className="text-2xl font-bold text-foreground">{cvData ? '1' : '0'}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-card backdrop-blur-sm rounded-2xl p-6 border border-border shadow-sm"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Analisis Selesai</p>
                <p className="text-2xl font-bold text-foreground">{cvData ? '1' : '0'}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-card backdrop-blur-sm rounded-2xl p-6 border border-border shadow-sm"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-accent" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Rekomendasi</p>
                <p className="text-2xl font-bold text-foreground">{cvData ? '3' : '0'}</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Main Action Card */}
        {cvData ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-secondary rounded-3xl p-8 text-secondary-foreground shadow-md"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 bg-secondary-foreground/10 backdrop-blur-sm rounded-full px-4 py-2 mb-4">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  <span className="text-sm font-medium">CV Tersimpan</span>
                </div>
                <h2 className="text-3xl font-bold mb-3">CV Anda Sudah Terupload</h2>
                <p className="text-secondary-foreground/80 mb-2">File: {cvData.fileName}</p>
                <p className="text-secondary-foreground/80 mb-6 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {new Date(cvData.uploadedAt).toLocaleDateString('id-ID', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })}
                </p>
                <div className="flex gap-4">
                  <button
                    onClick={() => router.push('/analysis')}
                    className="px-8 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 transition-all shadow-sm"
                  >
                    Lihat Hasil Analisis
                  </button>
                  <button
                    onClick={() => router.push('/upload')}
                    className="px-8 py-3 bg-secondary-foreground/10 backdrop-blur-sm rounded-xl font-medium hover:bg-secondary-foreground/20 transition-colors"
                  >
                    Upload CV Baru
                  </button>
                </div>
              </div>
              <div className="hidden md:block">
                <div className="w-32 h-32 bg-secondary-foreground/10 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                  <FileText className="w-16 h-16 text-primary" />
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-secondary rounded-3xl p-8 text-secondary-foreground shadow-md"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h2 className="text-3xl font-bold mb-3">Mulai Analisis CV Anda</h2>
                <p className="text-secondary-foreground/80 mb-6 max-w-2xl">
                  Upload CV Anda dan dapatkan analisis mendalam tentang skills, pengalaman, dan
                  rekomendasi pekerjaan yang paling cocok untuk profil Anda.
                </p>
                <button
                  onClick={() => router.push('/upload-cv')}
                  className="px-8 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 transition-all flex items-center gap-2 shadow-sm"
                >
                  <Upload className="w-5 h-5" />
                  Upload CV Sekarang
                </button>
              </div>
              <div className="hidden md:block">
                <div className="w-32 h-32 bg-secondary-foreground/10 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                  <Upload className="w-16 h-16 text-primary" />
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12"
        >
          <h3 className="text-xl font-bold mb-6 text-foreground">Aksi Cepat</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <button
              onClick={() => router.push('/upload-cv')}
              className="bg-card backdrop-blur-sm rounded-2xl p-6 border border-border hover:border-primary hover:shadow-md transition-all text-left group"
            >
              <div className="w-12 h-12 bg-secondary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Upload className="w-6 h-6 text-secondary" />
              </div>
              <h4 className="font-bold mb-2 text-foreground">Upload CV Baru</h4>
              <p className="text-sm text-muted-foreground">
                Upload atau perbarui CV Anda untuk mendapatkan analisis terbaru
              </p>
            </button>

            <button
              onClick={() => router.push('/analysis')}
              className="bg-card backdrop-blur-sm rounded-2xl p-6 border border-border hover:border-primary hover:shadow-md transition-all text-left group"
            >
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <BarChart3 className="w-6 h-6 text-primary" />
              </div>
              <h4 className="font-bold mb-2 text-foreground">Lihat Analisis</h4>
              <p className="text-sm text-muted-foreground">
                Tinjau hasil analisis dan rekomendasi pekerjaan untuk Anda
              </p>
            </button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}