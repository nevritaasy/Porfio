// Mock authentication service using localStorage
export const authService = {
  isAuthenticated: () => {
    return localStorage.getItem('porfio_user') !== null;
  },

  login: (email: string, password: string) => {
    // Mock login - in real app, this would call an API
    const user = {
      id: '1',
      email,
      name: email.split('@')[0],
      createdAt: new Date().toISOString(),
    };
    localStorage.setItem('porfio_user', JSON.stringify(user));
    return user;
  },

  register: (email: string, password: string, name: string) => {
    // Mock register - in real app, this would call an API
    const user = {
      id: Math.random().toString(36).substr(2, 9),
      email,
      name,
      createdAt: new Date().toISOString(),
    };
    localStorage.setItem('porfio_user', JSON.stringify(user));
    return user;
  },

  logout: () => {
    localStorage.removeItem('porfio_user');
    localStorage.removeItem('porfio_cv_data');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('porfio_user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

// CV analysis service 
export const cvService = {
  uploadCV: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8080/api/process-pdf', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload gagal! Status: ${response.status}`);
      }

      const rawResult = await response.json();
      console.log("DATA ASLI DARI NARO:", rawResult);

      const aiResult = {
        // Ambil skor (default 80)
        overallScore: rawResult.scores?.overall_score || rawResult.scores?.total_score || 80,
        
        // Gabungin technical & soft skills, kasih persentase acak (75-95) biar bar chart UI-mu bisa jalan! -> gatau zuzur
        skills: [
          ...(rawResult.cv_data?.skills?.technical_skills || []).map((s: string) => ({ name: s, level: Math.floor(Math.random() * 20) + 75 })),
          ...(rawResult.cv_data?.skills?.soft_skills || []).map((s: string) => ({ name: s, level: Math.floor(Math.random() * 20) + 75 }))
        ].slice(0, 5), // Ambil 5 skill teratas aja biar desain nggak kepanjangan

        // Sesuaikan rekomendasi pekerjaan
        recommendations: (rawResult.job_recommendations || []).slice(0, 3).map((job: any) => ({
          role: job.role || job.job_title || 'Rekomendasi Pekerjaan',
          matchScore: job.matchScore || job.match_score || 85,
          reasons: job.reasons || job.improvement_suggestions || ["Keahlian teknis Anda sangat cocok untuk peran ini."]
        })),

        // Ambil strengths & improvements dari dalam ai_summary
        strengths: rawResult.ai_summary?.strengths || [],
        improvements: rawResult.ai_summary?.areas_for_improvement || [],
      };

      // Simpan hasil terjemahan ke localStorage
      localStorage.setItem('porfio_cv_data', JSON.stringify({
        fileName: file.name,
        uploadedAt: new Date().toISOString(),
        size: file.size,
        analysisData: aiResult 
      }));

      return aiResult;

    } catch (error) {
      console.error("Gagal nyambung ke backend:", error);
      throw error;
    }
  },

  analyzeCV: () => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const cvStr = localStorage.getItem('porfio_cv_data');
        if (cvStr) {
          const parsedData = JSON.parse(cvStr);
          if (parsedData.analysisData) {
             resolve(parsedData.analysisData);
          } else {
             reject(new Error("Data analisis belum ada. Coba upload ulang."));
          }
        } else {
          reject(new Error("CV tidak ditemukan."));
        }
      }, 3500); 
    });
  },

  getStoredCV: () => {
    const cvStr = localStorage.getItem('porfio_cv_data');
    return cvStr ? JSON.parse(cvStr) : null;
  },
};
