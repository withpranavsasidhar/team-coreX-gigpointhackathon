import type {
  AgentStatus,
  AIInteractionRow,
  AriaChatResponse,
  AriaToolCall,
  Business,
  BusinessSummary,
  BusinessType,
  Customer,
  CustomerDetail,
  Expense,
  InventoryEvent,
  MemoryResult,
  MoneySummary,
  Product,
  ProductCreateInput,
  ProductHistory,
  Insights,
  LoginResponse,
  ProductStatus,
  QueryAnswer,
  StockAlert,
  Supplier,
  TypeDetection,
  VisionAnalysis as VisionAnalysisResult,
  VisionApplyResult,
  VisionStatus,
  VoiceCapabilities,
  VoiceInterpretation,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  code: string;
  details: Record<string, unknown>;

  constructor(message: string, code = "UNKNOWN", details: Record<string, unknown> = {}) {
    super(message);
    this.code = code;
    this.details = details;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const authHeaders: Record<string, string> = { "Content-Type": "application/json" };
  try {
    const raw = typeof window !== "undefined" ? localStorage.getItem("aria.user_session") : null;
    if (raw) {
      const user = JSON.parse(raw);
      if (user?.id) {
        authHeaders["X-User-Id"] = user.id;
      }
    }
  } catch {
    /* ignore */
  }

  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      ...options,
      headers: {
        ...authHeaders,
        ...((options.headers as Record<string, string>) || {}),
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError("Cannot reach the ARIA server. Is the backend running?", "NETWORK_ERROR");
  }


  if (!res.ok) {
    let payload: { error?: { code?: string; message?: string; details?: Record<string, unknown> }; detail?: string } = {};
    try {
      payload = await res.json();
    } catch {
      /* non-JSON error body */
    }
    const message = payload.error?.message || payload.detail || `Request failed (${res.status})`;
    const code = payload.error?.code || (res.status === 403 ? "FORBIDDEN" : res.status === 404 ? "NOT_FOUND" : "HTTP_ERROR");
    throw new ApiError(message, code, payload.error?.details ?? {});
  }


  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

const scoped = (businessId: string, path: string, extra = "") =>
  `${path}${path.includes("?") ? "&" : "?"}business_id=${businessId}${extra}`;

export const api = {
  currentBusiness: () => request<Business>("/businesses/current"),
  getBusiness: (id: string) => request<Business>(`/businesses/${id}`),

  register: (body: { name: string; phone: string; password: string; confirm_password: string }) =>
    request<LoginResponse>("/auth/register", { method: "POST", body: JSON.stringify(body) }),

  login: (body: { phone: string; password: string }) =>
    request<LoginResponse>("/auth/login", { method: "POST", body: JSON.stringify(body) }),

  userBusinesses: (userId: string) =>
    request<Business[]>(`/auth/user/${userId}/businesses`),

  createUserBusiness: (userId: string, body: { business_name: string; business_type: string; location?: string; seed_catalogue?: boolean; seed_demo_history?: boolean }) =>
    request<BusinessSummary>(`/auth/user/${userId}/businesses`, { method: "POST", body: JSON.stringify({ ...body, user_id: userId }) }),

  supportedUnits: () => request<{ units: string[] }>("/products/units"),

  inventory: (businessId: string) =>
    request<ProductStatus[]>(scoped(businessId, "/inventory")),

  productHistory: (businessId: string, productId: string, days = 30) =>
    request<ProductHistory>(scoped(businessId, `/inventory/${productId}/history`, `&days=${days}`)),

  createProduct: (businessId: string, body: ProductCreateInput) =>
    request<Product>(scoped(businessId, "/products"), {
      method: "POST",
      body: JSON.stringify(body),
    }),

  updateProduct: (businessId: string, productId: string, body: Partial<ProductCreateInput>) =>
    request<Product>(scoped(businessId, `/products/${productId}`), {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  archiveProduct: (businessId: string, productId: string) =>
    request<Product>(scoped(businessId, `/products/${productId}/archive`), { method: "POST" }),

  restoreProduct: (businessId: string, productId: string) =>
    request<Product>(scoped(businessId, `/products/${productId}/restore`), { method: "POST" }),

  events: (businessId: string, limit = 50) =>
    request<InventoryEvent[]>(scoped(businessId, "/events", `&limit=${limit}`)),

  createEvent: (
    businessId: string,
    body: {
      product_id: string;
      event_type: string;
      quantity: number;
      unit?: string;
      customer_name?: string;
      price?: number;
      source?: string;
      original_text?: string;
      normalized_text?: string;
      detected_language?: string;
      confidence?: number;
    }
  ) =>
    request<InventoryEvent>(scoped(businessId, "/events"), {
      method: "POST",
      body: JSON.stringify(body),
    }),

  voiceCapabilities: () => request<VoiceCapabilities>("/voice/capabilities"),

  alerts: (businessId: string) => request<StockAlert[]>(scoped(businessId, "/alerts")),

  insights: (businessId: string) => request<Insights>(scoped(businessId, "/analytics")),

  ask: (businessId: string, question: string, replyLanguage?: string) =>
    request<QueryAnswer>(scoped(businessId, "/query"), {
      method: "POST",
      body: JSON.stringify({ question, reply_language: replyLanguage ?? null }),
    }),

  processVoice: (
    businessId: string,
    transcript: string,
    languageHint?: string,
    replyLanguage?: string
  ) =>
    request<VoiceInterpretation>(scoped(businessId, "/voice/process"), {
      method: "POST",
      body: JSON.stringify({
        transcript,
        language_hint: languageHint ?? null,
        reply_language: replyLanguage ?? null,
      }),
    }),

  // ---------- Business context & onboarding ----------
  businessTypes: () => request<BusinessType[]>("/business-types"),

  detectBusinessType: (text: string) =>
    request<TypeDetection>("/business-types/detect", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  onboard: (body: {
    business_name: string;
    business_type?: string | null;
    spoken_description?: string | null;
    location?: string;
    default_language?: string;
    seed_catalogue?: boolean;
    seed_demo_history?: boolean;
  }) =>
    request<BusinessSummary>("/businesses/onboard", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  summary: (businessId: string) =>
    request<BusinessSummary>(scoped(businessId, "/businesses/summary")),

  adoptCatalogue: (businessId: string) =>
    request<BusinessSummary>(scoped(businessId, "/businesses/adopt-catalogue"), { method: "POST" }),

  seedDemo: (businessId: string) =>
    request<BusinessSummary>(scoped(businessId, "/businesses/seed-demo"), { method: "POST" }),

  units: (businessId: string) =>
    request<{ units: string[]; natural: string[] }>(scoped(businessId, "/units")),

  // ---------- Memory ----------
  memory: (
    businessId: string,
    filters: {
      q?: string;
      event_type?: string;
      product_id?: string;
      customer_id?: string;
      days?: number;
      limit?: number;
    } = {}
  ) => {
    const params = Object.entries(filters)
      .filter(([, v]) => v !== undefined && v !== null && v !== "")
      .map(([k, v]) => `&${k}=${encodeURIComponent(String(v))}`)
      .join("");
    return request<MemoryResult>(scoped(businessId, "/memory", params));
  },

  interactions: (businessId: string, limit = 20) =>
    request<{ interactions: AIInteractionRow[] }>(
      scoped(businessId, "/memory/interactions", `&limit=${limit}`)
    ),

  // ---------- People & money ----------
  customers: (businessId: string) => request<Customer[]>(scoped(businessId, "/customers")),

  customerDetail: (businessId: string, customerId: string) =>
    request<CustomerDetail>(scoped(businessId, `/customers/${customerId}`)),

  recordPayment: (businessId: string, customerId: string, amount: number, note = "") =>
    request<{ id: string; amount: number }>(
      scoped(businessId, `/customers/${customerId}/payments`),
      { method: "POST", body: JSON.stringify({ customer_id: customerId, amount, note }) }
    ),

  suppliers: (businessId: string) => request<Supplier[]>(scoped(businessId, "/suppliers")),

  createSupplier: (
    businessId: string,
    body: { name: string; phone?: string; supplies?: string; lead_time_days?: number }
  ) =>
    request<Supplier>(scoped(businessId, "/suppliers"), {
      method: "POST",
      body: JSON.stringify(body),
    }),

  deleteSupplier: (businessId: string, supplierId: string) =>
    request<void>(scoped(businessId, `/suppliers/${supplierId}`), { method: "DELETE" }),

  expenses: (businessId: string, days = 30) =>
    request<Expense[]>(scoped(businessId, "/expenses", `&days=${days}`)),

  createExpense: (businessId: string, body: { category: string; amount: number; note?: string }) =>
    request<Expense>(scoped(businessId, "/expenses"), {
      method: "POST",
      body: JSON.stringify(body),
    }),

  money: (businessId: string, days = 30) =>
    request<MoneySummary>(scoped(businessId, "/money", `&days=${days}`)),

  // ---------- A.R.I.A. agent (canonical conversational endpoint) ----------
  ariaStatus: () => request<AgentStatus>("/aria/status"),

  ariaChat: (
    businessId: string,
    message: string,
    options: { conversationId?: string | null; language?: string; source?: string } = {}
  ) =>
    request<AriaChatResponse>(scoped(businessId, "/aria/chat"), {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: options.conversationId ?? null,
        language: options.language ?? null,
        source: options.source ?? "text",
      }),
    }),

  // ---------- A.R.I.A. Vision ----------
  visionStatus: () => request<VisionStatus>("/aria/vision/status"),

  visionAnalyze: (businessId: string, imageDataUri: string, hint = "") =>
    request<VisionAnalysisResult>(scoped(businessId, "/aria/vision/analyze"), {
      method: "POST",
      body: JSON.stringify({ image: imageDataUri, hint }),
    }),

  visionApply: (
    businessId: string,
    analysisId: string,
    items: Record<string, unknown>[],
    action = "add_stock"
  ) =>
    request<VisionApplyResult>(scoped(businessId, "/aria/vision/apply"), {
      method: "POST",
      body: JSON.stringify({ analysis_id: analysisId, items, action }),
    }),

  ariaConfirm: (businessId: string, actionId: string, approved: boolean) =>
    request<{
      response: string;
      status: string;
      error: string | null;
      tool_calls: AriaToolCall[];
    }>(scoped(businessId, "/aria/confirm"), {
      method: "POST",
      body: JSON.stringify({ action_id: actionId, approved }),
    }),
};
