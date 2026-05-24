"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Mail, Lock, User, ArrowRight } from "lucide-react";
import { authService } from "../services/mockServices";

export default function Register() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      await authService.register(email, password, name);
      router.push("/dashboard");
    } catch (submitError) {
      setError(
        submitError instanceof Error ? submitError.message : "Gagal mendaftar.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <Link href="/" className="inline-flex items-center gap-2 mb-2">
            <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center shadow-sm">
              <span className="text-primary-foreground font-bold text-2xl">
                P
              </span>
            </div>
          </Link>
          <h1 className="text-3xl font-bold mt-4">Daftar ke Porfio</h1>
          <p className="text-foreground/70 mt-2">
            Mulai analisis CV Anda sekarang
          </p>
        </motion.div>

        {/* Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-card text-card-foreground rounded-2xl p-8 shadow-md border border-border"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                Nama Lengkap
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-white text-foreground rounded-xl border border-border focus:border-ring focus:ring-2 focus:ring-ring/50 outline-none transition-all"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-white text-foreground rounded-xl border border-border focus:border-ring focus:ring-2 focus:ring-ring/50 outline-none transition-all"
                  placeholder="nama@email.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-white text-foreground rounded-xl border border-border focus:border-ring focus:ring-2 focus:ring-ring/50 outline-none transition-all"
                  placeholder="••••••••"
                  required
                  minLength={6}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Minimal 6 karakter
              </p>
            </div>

            <label className="flex items-start gap-2 cursor-pointer">
              <input
                type="checkbox"
                className="w-4 h-4 mt-0.5 rounded border-border text-primary focus:ring-ring/50 outline-none"
                required
              />
              <span className="text-sm text-foreground/80">
                Saya setuju dengan{" "}
                <button
                  type="button"
                  className="text-primary hover:underline font-medium"
                >
                  Syarat & Ketentuan
                </button>{" "}
                dan{" "}
                <button
                  type="button"
                  className="text-primary hover:underline font-medium"
                >
                  Kebijakan Privasi
                </button>
              </span>
            </label>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-all flex items-center justify-center gap-2 disabled:opacity-50 font-medium shadow-sm"
            >
              {isLoading ? (
                "Memproses..."
              ) : (
                <>
                  Daftar Sekarang
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
          </form>

          <div className="mt-6 text-center text-sm text-foreground/70">
            Sudah punya akun?{" "}
            <Link
              href="/login"
              className="text-primary font-medium hover:underline"
            >
              Masuk di sini
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
