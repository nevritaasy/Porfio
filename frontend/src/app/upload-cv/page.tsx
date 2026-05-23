"use client";

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, FileText, X, CheckCircle2, Loader2, ArrowLeft } from 'lucide-react';
import { authService, cvService } from '../services/mockServices';

export default function UploadCV() {
  const router = useRouter();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [user, setUser] = useState<any>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      router.push('/login');
      return;
    }
    setUser(currentUser);
  }, [router]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    await cvService.uploadCV(file);
    setIsUploading(false);
    setUploadComplete(true);

    // Redirect ke halaman analisis setelah delay singkat
    setTimeout(() => {
      router.push('/analysis');
    }, 1500);
  };

  const removeFile = () => {
    setFile(null);
    setUploadComplete(false);
  };

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

      <main className="max-w-4xl mx-auto px-6 py-12">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-bold mb-3 text-foreground">Upload CV Anda</h1>
          <p className="text-xl text-muted-foreground mb-12">
            Upload CV dalam format PDF, DOCX, atau gambar untuk memulai analisis
          </p>
        </motion.div>

        {!uploadComplete ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            style={{ marginTop: '20px' }}
          >
            {/* Upload Area */}
            {!file ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{ padding: '48px', borderRadius: '24px', borderStyle: 'dashed', marginTop: '20px' }}
                className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all ${
                  isDragging
                    ? 'border-primary bg-primary/5'
                    : 'border-border bg-card shadow-sm'
                }`}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  onChange={handleFileChange}
                />
                <div className="w-20 h-20 bg-secondary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Upload className="w-10 h-10 text-secondary" />
                </div>
                <h3 className="text-xl font-bold mb-2 text-foreground">
                  {isDragging ? 'Lepaskan file di sini' : 'Drag & drop file CV Anda'}
                </h3>
                <p className="text-muted-foreground mb-6">atau</p>
                <label
                  htmlFor="file-upload"
                  className="inline-block px-8 py-3 bg-primary text-primary-foreground rounded-xl cursor-pointer hover:opacity-90 transition-all shadow-sm font-medium"
                >
                  Pilih File
                </label>
                <p className="text-sm text-muted-foreground mt-6">
                  Format yang didukung: PDF, DOCX, JPG, PNG (Maks. 10MB)
                </p>
              </div>
            ) : (
              <div className="bg-card rounded-3xl p-8 border border-border shadow-sm">
                {/* File Preview */}
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                    <FileText className="w-8 h-8 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0 text-left">
                    <h4 className="font-bold mb-1 truncate text-foreground">{file.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={removeFile}
                    className="p-2 hover:bg-muted rounded-lg transition-colors flex-shrink-0 text-muted-foreground"
                    disabled={isUploading}
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Upload Progress */}
                {isUploading && (
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-foreground">Mengupload...</span>
                      <span className="text-sm text-muted-foreground">Processing</span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: '100%' }}
                        transition={{ duration: 1.5, ease: 'easeInOut' }}
                        className="h-full bg-primary"
                      />
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-4">
                  <button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="flex-1 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Mengupload...
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        Upload & Analisis
                      </>
                    )}
                  </button>
                  <button
                    onClick={removeFile}
                    disabled={isUploading}
                    className="px-6 py-3 bg-background border border-border text-foreground rounded-xl font-medium hover:bg-muted transition-colors disabled:opacity-50"
                  >
                    Batal
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            style={{ padding: '48px', borderRadius: '24px', marginTop: '20px' }}
            className="bg-card rounded-3xl p-12 text-center border-2 border-primary/20 shadow-md"
          >
            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-10 h-10 text-primary" />
            </div>
            <h3 className="text-2xl font-bold mb-3 text-foreground">Upload Berhasil!</h3>
            <p className="text-muted-foreground mb-6">
              CV Anda telah berhasil diupload. Mengarahkan ke halaman analisis...
            </p>
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground font-medium">Memproses AI...</span>
            </div>
          </motion.div>
        )}

        {/* Info Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{ marginTop: '25px' }}
          className="grid md:grid-cols-3 gap-6 mt-12"
        >
          {/* Kotak 1: Aman & Privat */}
          <div className="bg-card rounded-2xl p-6 border border-border shadow-sm flex flex-col justify-center">
            <h4 className="font-bold mb-2 text-foreground text-left">Aman & Privat</h4>
            <p className="text-sm text-muted-foreground text-left">
              Data CV Anda terenkripsi dan tidak akan dibagikan kepada pihak ketiga
            </p>
          </div>

          {/* Kotak 2: Analisis Cepat */}
          <div className="bg-card rounded-2xl p-6 border border-border shadow-sm flex flex-col justify-center">
            <h4 className="font-bold mb-2 text-foreground text-left">Analisis Cepat</h4>
            <p className="text-sm text-muted-foreground text-left">
              Dapatkan hasil analisis mendalam dalam hitungan detik menggunakan AI
            </p>
          </div>

          {/* Kotak 3: Rekomendasi Akurat */}
          <div className="bg-card rounded-2xl p-6 border border-border shadow-sm flex flex-col justify-center">
            <h4 className="font-bold mb-2 text-foreground text-left">Rekomendasi Akurat</h4>
            <p className="text-sm text-muted-foreground text-left">
              Temukan peluang karir yang paling sesuai dengan profil dan keahlian Anda
            </p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}