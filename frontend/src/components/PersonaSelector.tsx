import { useEffect, useState } from 'react'
import { Users, Briefcase, MapPin, Loader2 } from 'lucide-react'
import { getDemoPersonas, type Persona } from '../api/client'

interface Props {
  selected: Persona | null
  onSelect: (persona: Persona) => void
}

const CATEGORY_COLORS: Record<string, string> = {
  'IT Professional': 'bg-blue-100 text-blue-700',
  'Banking & Finance': 'bg-green-100 text-green-700',
  Healthcare: 'bg-red-100 text-red-700',
  'Sales & Marketing': 'bg-orange-100 text-orange-700',
  'Self-Employed / Business': 'bg-purple-100 text-purple-700',
  'Government & Public Sector': 'bg-slate-100 text-slate-700',
  Education: 'bg-yellow-100 text-yellow-700',
  'Operations & Logistics': 'bg-teal-100 text-teal-700',
}

export function PersonaSelector({ selected, onSelect }: Props) {
  const [personas, setPersonas] = useState<Persona[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getDemoPersonas(6)
      .then((res) => setPersonas(res.personas))
      .catch(() => setError('Could not load demo personas.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading personas…
      </div>
    )
  }

  if (error) {
    return <p className="text-sm text-red-500">{error}</p>
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Users className="h-4 w-4 text-slate-400" />
        <span className="text-sm font-semibold text-slate-600">Select a Demo User</span>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {personas.map((persona) => {
          const isSelected = selected?.id === persona.id
          return (
            <button
              key={persona.id}
              onClick={() => onSelect(persona)}
              className={`rounded-xl border p-4 text-left transition
                ${isSelected
                  ? 'border-blue-400 bg-blue-50 ring-2 ring-blue-200'
                  : 'border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50'
                }`}
            >
              <div className="mb-2 flex items-start justify-between gap-2">
                <p className="text-sm font-semibold text-slate-800">{persona.full_name}</p>
                <span
                  className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${CATEGORY_COLORS[persona.occupation_category] ?? 'bg-slate-100 text-slate-600'}`}
                >
                  {persona.occupation_category}
                </span>
              </div>
              <div className="flex items-center gap-1 text-xs text-slate-500">
                <Briefcase className="h-3 w-3" />
                <span className="truncate">{persona.occupation}</span>
              </div>
              <div className="mt-0.5 flex items-center gap-1 text-xs text-slate-400">
                <MapPin className="h-3 w-3" />
                <span>
                  {persona.city}, {persona.state}
                </span>
              </div>
            </button>
          )
        })}
      </div>

      {selected && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <p className="mb-1 font-semibold">Demo Scenario</p>
          <p>{selected.demo_scenario}</p>
          <p className="mt-2 text-xs text-amber-700">
            <strong>Insurance considerations:</strong> {selected.insurance_profile}
          </p>
        </div>
      )}
    </div>
  )
}
