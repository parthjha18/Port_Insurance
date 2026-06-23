import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Loader2, CheckCircle, AlertCircle, X } from 'lucide-react'
import type { UseUploadResult } from '../hooks/useUpload'

interface Props {
  label: string
  result: UseUploadResult
}

export function DocumentUpload({ label, result }: Props) {
  const { stage, uploadResponse, benefits, error, upload, reset } = result

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles[0]) upload(acceptedFiles[0])
    },
    [upload],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: stage === 'uploading' || stage === 'analyzing',
  })

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">{label}</h3>

      {stage === 'idle' || stage === 'error' ? (
        <div
          {...getRootProps()}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-10 transition
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'}`}
        >
          <input {...getInputProps()} />
          <Upload className="mb-3 h-8 w-8 text-slate-400" />
          <p className="text-sm font-medium text-slate-600">
            {isDragActive ? 'Drop the PDF here' : 'Drag & drop a PDF, or click to browse'}
          </p>
          <p className="mt-1 text-xs text-slate-400">Max 50 MB · PDF only</p>
        </div>
      ) : null}

      {(stage === 'uploading' || stage === 'analyzing') && (
        <div className="flex flex-col items-center gap-3 py-8">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-sm text-slate-600">
            {stage === 'uploading' ? 'Uploading PDF…' : 'Parsing PDF and extracting benefits with AI…'}
          </p>
        </div>
      )}

      {stage === 'done' && uploadResponse && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
            <CheckCircle className="h-4 w-4 shrink-0" />
            <span>
              <strong>{uploadResponse.filename}</strong> — {uploadResponse.pages_extracted} pages,{' '}
              {uploadResponse.chunks_indexed} chunks indexed
            </span>
            <button onClick={reset} className="ml-auto text-slate-400 hover:text-slate-600">
              <X className="h-4 w-4" />
            </button>
          </div>

          {benefits && (
            <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
              <p className="font-semibold text-slate-700">{benefits.insurer_name ?? 'Unknown Insurer'}</p>
              <div className="mt-1 grid grid-cols-2 gap-x-4 gap-y-1">
                {benefits.sum_insured != null && (
                  <span>Sum Insured: ₹{(benefits.sum_insured / 100000).toFixed(1)}L</span>
                )}
                {benefits.annual_premium != null && (
                  <span>Premium: ₹{benefits.annual_premium.toLocaleString('en-IN')}/yr</span>
                )}
                {benefits.waiting_period_years != null && (
                  <span>Waiting: {benefits.waiting_period_years}yr</span>
                )}
                {benefits.no_claim_bonus_pct != null && (
                  <span>NCB: {benefits.no_claim_bonus_pct}%</span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {stage === 'error' && error && (
        <div className="mt-3 flex items-start gap-2 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Hidden file icon for visual context when not uploading */}
      {stage === 'idle' && (
        <div className="mt-3 flex items-center gap-2 text-xs text-slate-400">
          <FileText className="h-3 w-3" />
          <span>Policy document, portability kit, or renewal notice</span>
        </div>
      )}
    </div>
  )
}
