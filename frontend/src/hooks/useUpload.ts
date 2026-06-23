import { useState } from 'react'
import { uploadPolicy, type UploadResponse, type PolicyBenefits } from '../api/client'

export type UploadStage = 'idle' | 'uploading' | 'done' | 'error'

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
      // Single fast call: PDF → text → regex extraction → embed (~5-10s, no LLM)
      const upRes = await uploadPolicy(file)
      setUploadResponse(upRes)
      if (upRes.benefits) setBenefits(upRes.benefits)
      setStage('done')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string }
      const detail = axiosErr?.response?.data?.detail
      setError(detail ?? axiosErr?.message ?? 'Upload failed. Please try again.')
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
