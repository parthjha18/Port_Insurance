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
      // Upload returns benefits inline — no extra /analyze round trip needed
      setStage('analyzing')
      const upRes = await uploadPolicy(file)
      setUploadResponse(upRes)

      if (upRes.benefits) {
        // Benefits already extracted during upload (happy path)
        setBenefits(upRes.benefits)
        setStage('done')
      } else {
        // Fallback: call /analyze separately (e.g. if inline extraction failed)
        try {
          const benefitsRes = await analyzePolicy(upRes.collection_id)
          setBenefits(benefitsRes)
        } catch {
          // Non-fatal — still show the upload success without benefits preview
          console.warn('Benefit extraction failed. Analysis will run on Compare/Chat.')
        }
        setStage('done')
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Upload failed. Please try again.'
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
