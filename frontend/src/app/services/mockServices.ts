type BackendUser = {
  id: string;
  name: string;
  email: string;
  createdAt?: string;
};

export type NormalizedAnalysis = {
  overallScore: number;
  skills: Array<{ name: string; level: number }>;
  recommendations: Array<{
    role: string;
    matchScore: number;
    reasons: string[];
  }>;
  strengths: string[];
  improvements: string[];
  uploadedAt?: string;
};

type JobRecommendationPayload = {
  role?: string;
  job_title?: string;
  matchScore?: number | string;
  match_score?: number | string;
  reasons?: unknown[];
  improvement_suggestions?: unknown[];
  reason?: string;
};

type AnalysisRecord = {
  scores?: {
    overall_score?: number | string;
    total_score?: number | string;
    overallScore?: number | string;
  };
  cv_data?: {
    skills?: {
      technical_skills?: unknown[];
      soft_skills?: unknown[];
    };
  };
  ai_summary?: {
    strengths?: unknown[];
    areas_for_improvement?: unknown[];
  };
  job_recommendations?: unknown[];
  createdAt?: string;
};

type AnalysisResponse = {
  analysis?: {
    content?: AnalysisRecord;
    createdAt?: string;
  };
  content?: AnalysisRecord;
  createdAt?: string;
  cv_data?: AnalysisRecord["cv_data"];
  ai_summary?: AnalysisRecord["ai_summary"];
  job_recommendations?: unknown[];
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isAnalysisResponse(
  payload: AnalysisResponse | AnalysisRecord | null | undefined,
): payload is AnalysisResponse {
  return (
    isRecord(payload) &&
    ("analysis" in payload || "content" in payload || "createdAt" in payload)
  );
}

function resolveApiBaseUrl(): string {
  const configuredBase = (
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    ""
  ).trim();

  if (!configuredBase) {
    return typeof window !== "undefined" ? "/api" : "http://localhost:8080";
  }

  if (typeof window !== "undefined") {
    try {
      const resolvedUrl = new URL(configuredBase, window.location.origin);
      const isInternalDockerHost =
        resolvedUrl.hostname === "backend" ||
        resolvedUrl.hostname === "frontend" ||
        resolvedUrl.hostname === "ollama";

      if (isInternalDockerHost) {
        return "/api";
      }

      return resolvedUrl.toString().replace(/\/$/, "");
    } catch {
      return configuredBase.replace(/\/$/, "");
    }
  }

  return configuredBase.replace(/\/$/, "");
}

const API_BASE_URL = resolveApiBaseUrl();

async function requestJson<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    ...options,
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      payload?.error || `Request failed with status ${response.status}`,
    );
  }

  return payload as T;
}

function toNumber(value: unknown, fallback: number): number {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function normalizeReasons(job: unknown): string[] {
  const recommendation = isRecord(job) ? (job as JobRecommendationPayload) : {};

  if (Array.isArray(recommendation.reasons)) {
    return recommendation.reasons.filter(
      (reason: unknown) => typeof reason === "string" && reason.trim(),
    ) as string[];
  }

  if (Array.isArray(recommendation.improvement_suggestions)) {
    return recommendation.improvement_suggestions.filter(
      (reason: unknown) => typeof reason === "string" && reason.trim(),
    ) as string[];
  }

  if (
    typeof recommendation.reason === "string" &&
    recommendation.reason.trim()
  ) {
    return [recommendation.reason.trim()];
  }

  return ["Keahlian Anda relevan untuk peran ini."];
}

function normalizeAnalysis(
  payload: AnalysisResponse | AnalysisRecord | null | undefined,
): NormalizedAnalysis {
  const responsePayload = isAnalysisResponse(payload) ? payload : undefined;
  const recordPayload = isRecord(payload)
    ? (payload as AnalysisRecord)
    : undefined;

  const analysisPayload =
    responsePayload?.analysis?.content ??
    responsePayload?.content ??
    recordPayload ??
    {};
  const scores = analysisPayload?.scores ?? {};
  const cvData = analysisPayload?.cv_data ?? responsePayload?.cv_data ?? {};
  const aiSummary =
    analysisPayload?.ai_summary ?? responsePayload?.ai_summary ?? {};
  const jobRecommendations =
    analysisPayload?.job_recommendations ??
    responsePayload?.job_recommendations ??
    [];

  const overallScore = toNumber(
    scores?.overall_score ?? scores?.total_score ?? scores?.overallScore,
    80,
  );

  const baseSkills = [
    ...((cvData?.skills?.technical_skills ?? []) as string[]),
    ...((cvData?.skills?.soft_skills ?? []) as string[]),
  ]
    .filter((skill) => typeof skill === "string" && skill.trim())
    .slice(0, 5);

  const skills = baseSkills.map((name, index) => ({
    name,
    level: Math.max(
      45,
      Math.min(95, Math.round(overallScore) + 18 - index * 6),
    ),
  }));

  return {
    overallScore,
    skills,
    recommendations: (Array.isArray(jobRecommendations)
      ? jobRecommendations
      : []
    )
      .slice(0, 3)
      .map((job) => {
        const recommendation = isRecord(job)
          ? (job as JobRecommendationPayload)
          : {};

        return {
          role:
            recommendation.role ||
            recommendation.job_title ||
            "Rekomendasi Pekerjaan",
          matchScore: toNumber(
            recommendation.matchScore ?? recommendation.match_score,
            85,
          ),
          reasons: normalizeReasons(job),
        };
      }),
    strengths: Array.isArray(aiSummary?.strengths)
      ? aiSummary.strengths.filter((item: unknown) => typeof item === "string")
      : [],
    improvements: Array.isArray(aiSummary?.areas_for_improvement)
      ? aiSummary.areas_for_improvement.filter(
          (item: unknown) => typeof item === "string",
        )
      : [],
    uploadedAt:
      responsePayload?.analysis?.createdAt ??
      responsePayload?.createdAt ??
      analysisPayload?.createdAt ??
      undefined,
  };
}

export const authService = {
  isAuthenticated: async () => {
    return (await authService.getCurrentUser()) !== null;
  },

  login: async (email: string, password: string) => {
    const payload = await requestJson<{ user: BackendUser }>(
      "/api/auth/login",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      },
    );

    return payload.user;
  },

  register: async (email: string, password: string, name: string) => {
    const payload = await requestJson<{ user: BackendUser }>(
      "/api/auth/register",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email, password }),
      },
    );

    return payload.user;
  },

  logout: async () => {
    try {
      await requestJson<{ message: string }>("/api/auth/logout", {
        method: "POST",
      });
    } finally {
      localStorage.removeItem("porfio_user");
      localStorage.removeItem("porfio_cv_data");
    }
  },

  getCurrentUser: async (): Promise<BackendUser | null> => {
    try {
      const payload = await requestJson<{ user: BackendUser }>("/api/user/me");
      return payload.user;
    } catch {
      return null;
    }
  },
};

export const cvService = {
  uploadCV: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const rawResult = await requestJson<AnalysisResponse>("/api/process-pdf", {
      method: "POST",
      body: formData,
    });

    const normalized = normalizeAnalysis(rawResult);

    localStorage.setItem(
      "porfio_cv_data",
      JSON.stringify({
        fileName: file.name,
        uploadedAt: normalized.uploadedAt || new Date().toISOString(),
        size: file.size,
        analysisData: normalized,
      }),
    );

    return normalized;
  },

  analyzeCV: async () => {
    const latestAnalysis = await cvService.getLatestAnalysis();

    if (!latestAnalysis) {
      throw new Error("CV tidak ditemukan.");
    }

    return latestAnalysis;
  },

  getLatestAnalysis: async (): Promise<NormalizedAnalysis | null> => {
    try {
      const payload = await requestJson<AnalysisResponse>(
        "/api/user/own/latest",
      );

      return normalizeAnalysis(payload);
    } catch {
      return null;
    }
  },

  getStoredCV: async () => {
    const cvStr = localStorage.getItem("porfio_cv_data");
    if (cvStr) {
      return JSON.parse(cvStr);
    }

    const latestAnalysis = await cvService.getLatestAnalysis();
    return latestAnalysis
      ? {
          uploadedAt: latestAnalysis.uploadedAt,
          analysisData: latestAnalysis,
        }
      : null;
  },
};
