import axios from 'axios'

const BASE_URL = '/api'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
})

// ─── Types ────────────────────────────────────────────────────────────────────

export interface UploadResponse {
  collection_id: string
  filename: string
  pages_extracted: number
  chunks_indexed: number
  message: string
}

export interface PolicyBenefits {
  insurer_name?: string | null
  policy_number?: string | null
  sum_insured?: number | null
  annual_premium?: number | null
  waiting_period_years?: number | null
  pre_existing_covered?: boolean | null
  no_claim_bonus_pct?: number | null
  co_pay_pct?: number | null
  room_rent_cap?: string | null
  maternity_covered?: boolean | null
  restoration_benefit?: boolean | null
  day_care_procedures?: boolean | null
  ayush_treatment?: boolean | null
  ambulance_cover?: string | null
  policy_tenure_years?: number | null
  family_floater?: boolean | null
  claim_history_notes?: string | null
}

export interface BenefitDiff {
  field: string
  old_value?: string | null
  new_value?: string | null
  change_type: 'improved' | 'degraded' | 'unchanged' | 'unknown'
  notes?: string | null
}

export interface PortingComparison {
  old_policy: PolicyBenefits
  new_policy: PolicyBenefits
  diffs: BenefitDiff[]
  premium_delta?: number | null
  coverage_delta?: number | null
  recommendation: string
  cost_effective: boolean
  waiting_period_risk: string
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatResponse {
  answer: string
  sources: string[]
}

export interface Persona {
  id: string
  full_name: string
  occupation: string
  city: string
  state: string
  occupation_category: string
  insurance_profile: string
  demo_scenario: string
}

export interface PersonaListResponse {
  personas: Persona[]
  total: number
}

// ─── API Functions ─────────────────────────────────────────────────────────────

export async function uploadPolicy(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post<UploadResponse>('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function analyzePolicy(collectionId: string): Promise<PolicyBenefits> {
  const res = await api.post<PolicyBenefits>('/analyze', { collection_id: collectionId })
  return res.data
}

export async function comparePolicies(
  oldCollectionId: string,
  newCollectionId: string,
  personaId?: string,
): Promise<PortingComparison> {
  const res = await api.post<PortingComparison>('/analyze/compare', {
    old_collection_id: oldCollectionId,
    new_collection_id: newCollectionId,
    persona_id: personaId,
  })
  return res.data
}

export async function chatWithPolicy(
  collectionId: string,
  messages: ChatMessage[],
  personaId?: string,
): Promise<ChatResponse> {
  const res = await api.post<ChatResponse>('/chat', {
    collection_id: collectionId,
    messages,
    persona_id: personaId,
  })
  return res.data
}

export async function getDemoPersonas(limit = 5): Promise<PersonaListResponse> {
  const res = await api.get<PersonaListResponse>('/personas/demo', { params: { limit } })
  return res.data
}

export async function checkHealth(): Promise<{ status: string }> {
  const res = await api.get('/health')
  return res.data
}
