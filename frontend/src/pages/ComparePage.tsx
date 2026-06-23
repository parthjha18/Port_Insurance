import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2, GitCompare } from 'lucide-react'
import { comparePolicies, type PortingComparison } from '../api/client'
import { BenefitComparisonTable } from '../components/BenefitComparisonTable'

interface LocationState {
  oldCollectionId: string
  newCollectionId: string
  personaId?: string
}

export function ComparePage() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null

  const [comparison, setComparison] = useState<PortingComparison | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!state?.oldCollectionId || !state?.newCollectionId) return

    setLoading(true)
    comparePolicies(state.oldCollectionId, state.newCollectionId, state.personaId)
      .then(setComparison)
      .catch((err) =>
        setError(err instanceof Error ? err.message : 'Comparison failed. Please try again.'),
      )
      .finally(() => setLoading(false))
  }, [state?.oldCollectionId, state?.newCollectionId, state?.personaId])

  if (!state?.oldCollectionId) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <p className="text-slate-500">No policies selected for comparison.</p>
        <button
          onClick={() => navigate('/upload')}
          className="rounded-xl bg-blue-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-600"
        >
          Upload Policies
        </button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 px-4 py-10">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1 rounded-lg px-2 py-1.5 text-sm text-slate-500 hover:bg-slate-100"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
        <div className="flex items-center gap-2">
          <GitCompare className="h-5 w-5 text-blue-500" />
          <h1 className="text-xl font-bold text-slate-800">Policy Comparison</h1>
        </div>
      </div>

      {loading && (
        <div className="flex flex-col items-center gap-3 py-16">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-sm text-slate-500">
            Analyzing both policies and generating comparison…
          </p>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {comparison && !loading && <BenefitComparisonTable comparison={comparison} />}
    </div>
  )
}
