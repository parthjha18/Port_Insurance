import { useState } from 'react'
import { uploadPolicy, analyzePolicy, type UploadResponse, type PolicyBenefits } from '../api/client'

export type UploadStage = 'idle' | 'uploading' | 'analyzing' | 'done' | 'error'

export interface UseUploadResult {
  stage: UploadStage
  uploadResponse: UploadResponse | null
  benefits: PolicyBenefits | null
  error: string | null
  upload: (file: File) => Promise<void>
  reset: () => void
}

export function useUpload(): UseUploadResult {
  const [stage, setStage] = useState<UploadStage>('idle')
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null)
  const [benefits, setBenefits] = useState<PolicyBenefits | null>(null)
  const [error, setError] = useState<string | null>(null)

  const upload = async (file: File) => {
    setStage('uploading')
    setError(null)
    setUploadResponse(null)
    setBenefits(null)

    try {
      // Step 1 — fast: save PDF, extract text, embed into ChromaDB (~5-10s)
      const upRes = await uploadPolicy(file)
      setUploadResponse(upRes)

      // Step 2 — slow: GPT-4o mini extracts structured benefits (~30-90s)
      setStage('analyzing')
      const benefitsRes = await analyzePolicy(upRes.collection_id)
      setBenefits(benefitsRes)
      setStage('done')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string }
      const detail = axiosErr?.response?.data?.detail
      const msg = detail ?? axiosErr?.message ?? 'Something went wrong. Please try again.'
      setError(msg)
      setStage('error')
    }
  }

  const reset = () => {
    setStage('idle')
    setUploadResponse(null)
    setBenefits(null)
    setError(null)
  }

  return { stage, uploadResponse, benefits, error, upload, reset }
}
