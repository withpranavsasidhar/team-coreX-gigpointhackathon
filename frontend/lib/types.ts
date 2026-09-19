export type EventType =
  | "STOCK_IN"
  | "PURCHASE"
  | "RETURN"
  | "SALE"
  | "STOCK_OUT"
  | "CREDIT_SALE"
  | "DAMAGE"
  | "LOSS"
  | "ADJUSTMENT";

export type StockStatus = "healthy" | "low" | "critical" | "out_of_stock";

export interface User {
  id: string;
  name: string;
  phone: string;
  email: string;
  preferred_language: string;
}

export interface Business {
  id: string;
  owner_id?: string | null;
  business_name: string;
  business_type: string;
  location: string;
  default_language: string;
}

export interface LoginResponse {
  user: User;
  businesses: Business[];
}

export interface UnitConversion {
  id?: string;
  unit_name: string;
  factor_to_base_unit: number;
}

export interface Product {
  id: string;
  business_id: string;
  name: string;
  category: string;
  base_unit: string;
  current_quantity: number;
  minimum_quantity: number;
  reorder_quantity: number;
  price: number;
  is_archived: boolean;
  conversions: UnitConversion[];
}

export interface ProductStatus extends Product {
  status: StockStatus;
  avg_daily_usage: number;
  estimated_days_to_stockout: number | null;
  last_movement_at: string | null;
}

export interface InventoryEvent {
  id: string;
  product_id: string;
  product_name: string | null;
  customer_id: string | null;
  customer_name: string | null;
  event_type: EventType;
  quantity: number;
  unit: string;
  delta: number;
  price: number | null;
  payment_status: "PAID" | "CREDIT" | "NA";
  due_date: string | null;
  source: string;
  original_text: string;
  normalized_text: string;
  detected_language: string;
  confidence: number;
  occurred_at: string;
}

export interface MovementBreakdown {
  event_type: EventType;
  net_change: number;
  count: number;
}

export interface ProductHistory {
  product: ProductStatus;
  window_days: number;
  opening_balance: number;
  total_in: number;
  total_out: number;
  breakdown: MovementBreakdown[];
  events: InventoryEvent[];
}

export type VoiceStatus =
  | "recorded"
  | "amended"
  | "needs_confirmation"
  | "needs_clarification"
  | "rejected";

export interface ProductCandidate {
  product_id: string;
  name: string;
  base_unit: string;
  current_quantity: number;
  score: number;
}

export interface VoiceInterpretation {
  status: VoiceStatus;
  message: string;
  transcript: string;
  event_type: EventType | null;
  product_id: string | null;
  product_name: string | null;
  candidates: ProductCandidate[];
  quantity: number | null;
  unit: string | null;
  customer_name: string | null;
  price: number | null;
  payment_status: "PAID" | "CREDIT" | "NA";
  due_date: string | null;
  confidence: number;
  model_confidence: number;
  match_confidence: number;
  normalized_text: string;
  detected_language: string;
  reply_language: string;
  provider: string;
  notes: string[];
  created_event: InventoryEvent | null;
  resulting_quantity: number | null;
  resulting_unit: string | null;
  /** Set when this turn corrected the previous one. */
  amended_from?: number | null;
}

// ---------- Business context ----------
export interface BusinessType {
  key: string;
  label: string;
  descriptor: string;
  emoji: string;
  units: string[];
  categories: string[];
  sample_utterances: string[];
  starter_product_count: number;
  starter_product_names: string[];
}

export interface BusinessSummary {
  id: string;
  business_name: string;
  business_type: string;
  type_label: string;
  type_emoji: string;
  descriptor: string;
  location: string;
  default_language: string;
  units: string[];
  categories: string[];
  sample_utterances: string[];
  product_count: number;
  event_count: number;
  is_configured: boolean;
}

export interface TypeDetection {
  matched: boolean;
  key: string | null;
  label: string | null;
  descriptor?: string;
  emoji?: string;
  starter_product_names?: string[];
  units?: string[];
  text: string;
}

// ---------- A.R.I.A. Vision ----------
export interface VisionStatus {
  provider: string;
  model: string | null;
  available: boolean;
  reason: string | null;
  max_image_mb: number;
  accepted_types: string[];
}

export interface VisionCandidate {
  product_id: string;
  product_name: string;
  base_unit: string;
  current_quantity: number;
  score: number;
}

export interface VisionItem {
  raw_name: string;
  normalized_name: string;
  quantity: number | null;
  unit: string | null;
  price: number | null;
  confidence: number;
  confidence_band: "high" | "medium" | "low";
  item_note: string;
  product_id: string | null;
  product_name: string | null;
  base_unit: string | null;
  current_quantity: number | null;
  match_score: number;
  match_state: "matched" | "ambiguous" | "unmatched";
  candidates: VisionCandidate[];
  issues: string[];
  /** Nothing in the catalogue matched convincingly — offer to create it. */
  suggest_create: boolean;
  ready: boolean;
}

export interface VisionAnalysis {
  analysis_id?: string;
  document_type?: string;
  language?: string;
  readable?: boolean;
  quality_issues?: string[];
  quality_advice?: string[];
  notes?: string;
  items: VisionItem[];
  invoice?: Record<string, unknown> | null;
  summary: string;
  counts: { total: number; ready: number; needs_attention: number };
  provider?: string;
  model?: string;
  status?: string;
  /** Set when analysis could not run. Never accompanied by invented items. */
  error?: string;
  available?: boolean;
}

export interface VisionApplyResult {
  analysis_id?: string;
  action?: string;
  applied: {
    product: string;
    quantity: number;
    unit: string;
    applied_change: number;
    resulting_quantity: number;
    resulting_unit: string;
  }[];
  failed: { line: Record<string, unknown>; error: string }[];
  counts: { applied: number; failed: number };
  summary: string;
  error?: string;
}

// ---------- Memory ----------
export interface MemoryEvent {
  id: string;
  product_id: string;
  product_name: string;
  base_unit: string;
  customer_name: string | null;
  event_type: EventType;
  quantity: number;
  unit: string;
  delta: number;
  price: number | null;
  payment_status: "PAID" | "CREDIT" | "NA";
  due_date: string | null;
  source: string;
  original_text: string;
  normalized_text: string;
  detected_language: string;
  confidence: number;
  occurred_at: string;
}

export interface MemoryResult {
  events: MemoryEvent[];
  total: number;
  filters_applied: Record<string, unknown>;
}

export interface AIInteractionRow {
  id: string;
  kind: string;
  transcript: string;
  normalized_text: string;
  detected_language: string;
  intent: string;
  status: string;
  confidence: number;
  provider: string;
  response_text: string;
  source: string;
  event_id: string | null;
  created_at: string;
}

// ---------- People & money ----------
export interface Customer {
  id: string;
  name: string;
  phone: string;
  outstanding_credit: number;
}

export interface CustomerTotal {
  product_name: string;
  base_unit: string;
  quantity: number;
  count: number;
}

export interface CustomerDetail {
  customer: Customer & { created_at: string };
  totals: CustomerTotal[];
  lifetime_value: number;
  total_paid: number;
  transaction_count: number;
  events: MemoryEvent[];
  payments: { id: string; amount: number; note: string; occurred_at: string }[];
}

export interface Supplier {
  id: string;
  name: string;
  phone: string;
  supplies: string;
  lead_time_days: number;
}

export interface Expense {
  id: string;
  category: string;
  amount: number;
  note: string;
  occurred_at: string;
}

export interface MoneySummary {
  window_days: number;
  expenses_total: number;
  payments_received: number;
  expenses_by_category: { category: string; amount: number }[];
}

export interface VoiceCapabilities {
  ai_provider: string;
  llm_enabled: boolean;
  stt_provider: string;
  stt_is_client_side: boolean;
  confidence_threshold: number;
  clarification_threshold: number;
  degraded_reason: string | null;
  supported_languages: string[];
  agent_available: boolean;
  agent_model: string | null;
  translation_provider: string;
  translation_available: boolean;
}

// ---------- A.R.I.A. agent ----------
export interface AgentStatus {
  provider: string;
  model: string;
  is_llm: boolean;
  agent_available: boolean;
  configured: boolean;
  reason: string | null;
}

export interface PendingAction {
  id: string;
  tool: string;
  summary: string;
  arguments: Record<string, unknown>;
}

export interface AriaToolCall {
  tool: string;
  arguments: Record<string, unknown>;
  result: Record<string, any>;
}

export interface AriaChatResponse {
  response: string;
  conversation_id: string | null;
  language: string;
  tool_calls: AriaToolCall[];
  requires_confirmation: boolean;
  pending_action: PendingAction | null;
  status: "completed" | "needs_confirmation" | "needs_clarification" | "error" | "unavailable";
  error: string | null;
  /** Which engine actually answered — never guessed by the client. */
  engine: "agent" | "rule_engine";
  provider: string;
  model: string | null;
  notice?: string | null;
  /** Present on rule-engine question turns, so answers still render visually. */
  answer_payload?: QueryAnswer;
  /** Present on rule-engine command turns. */
  interpretation?: VoiceInterpretation;
}

export interface ProductCreateInput {
  name: string;
  category: string;
  base_unit: string;
  opening_stock: number;
  minimum_quantity: number;
  reorder_quantity: number;
  price: number;
  conversions: { unit_name: string; factor_to_base_unit: number }[];
}

export type QueryVisual = "stock" | "list" | "breakdown" | "timeline" | "none";

export interface QueryAnswer {
  intent: string;
  answer: string;
  visual: QueryVisual;
  items: Record<string, any>[];
  facts: Record<string, any>;
  product_id: string | null;
  product_name: string | null;
  window_label: string | null;
  grounded_by: string;
}

export interface StockAlert {
  product_id: string;
  product_name: string;
  alert_type: string;
  severity: "critical" | "warning" | "info";
  status: StockStatus;
  current_quantity: number;
  base_unit: string;
  minimum_quantity: number;
  avg_daily_usage: number;
  estimated_days_to_stockout: number | null;
  message: string;
}

export interface ReorderSuggestion {
  product_id: string;
  product_name: string;
  base_unit: string;
  current_quantity: number;
  minimum_quantity: number;
  target_quantity: number;
  suggested_quantity: number;
  avg_daily_usage: number;
  reason: string;
}

export interface UnusualMovement {
  product_id: string;
  product_name: string;
  base_unit: string;
  direction: "spike" | "slump";
  recent_quantity: number;
  prior_quantity: number;
  ratio: number;
  message: string;
}

export interface Mover {
  product_id: string;
  product_name: string;
  base_unit: string;
  avg_daily_usage: number;
  current_quantity: number;
}

export interface Insights {
  alerts: StockAlert[];
  reorder_recommendations: ReorderSuggestion[];
  unusual_movement: UnusualMovement[];
  fast_moving: Mover[];
  slow_moving: Mover[];
}
