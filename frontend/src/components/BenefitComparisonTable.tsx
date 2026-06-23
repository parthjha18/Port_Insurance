import { TrendingUp, TrendingDown, Minus, HelpCircle, AlertTriangle, CheckCircle } from 'lucide-react'
import type { PortingComparison } from '../api/client'

interface Props {
  comparison: PortingComparison
}

const CHANGE_ICONS = {
  improved: <TrendingUp className="h-4 w-4 text-green-500" />,
  degraded: <TrendingDown className="h-4 w-4 text-red-500" />,
  unchanged: <Minus className="h-4 w-4 text-slate-400" />,
  unknown: <HelpCircle className="h-4 w-4 text-slate-300" />,
}

const CHANGE_ROW_BG = {
  improved: 'bg-green-50',
  degraded: 'bg-red-50',
  unchanged: '',
  unknown: '',
}

function formatValue(v: string | null | undefined, fieldName = ''): string {
  if (v == null || v === '' || v === 'null') return '—'
  if (v === 'true') return 'Yes'
  if (v === 'false') return 'No'

  // Convert fractional years to a human-readable string
  if (fieldName.toLowerCase().includes('year')) {
    const num = parseFloat(v)
    if (!isNaN(num)) {
      if (num === 0) return 'None'
      if (num < 1) {
        const months = Math.round(num * 12)
        return months <= 1 ? '~1 month' : `~${months} months`
      }
      return `${num} year${num === 1 ? '' : 's'}`
    }
  }
  return v
}

export function BenefitComparisonTable({ comparison }: Props) {
  const { diffs, premium_delta, coverage_delta, recommendation, cost_effective, waiting_period_risk } =
    comparison

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <SummaryCard
          label="AI Verdict"
          value={
            recommendation.toLowerCase().includes('advisable') ||
            recommendation.toLowerCase().includes('recommend') ||
            recommendation.toLowerCase().includes('port')
              ? 'Port ✓'
              : cost_effective
                ? 'Port ✓'
                : 'Stay'
          }
          positive={
            recommendation.toLowerCase().includes('advisable') ||
            recommendation.toLowerCase().includes('recommend') ||
            recommendation.toLowerCase().includes('port') ||
            cost_effective
          }
        />
        <SummaryCard
          label="Premium Change"
          value={
            premium_delta != null
              ? `${premium_delta >= 0 ? '+' : ''}₹${Math.abs(premium_delta).toLocaleString('en-IN')}/yr`
              : '—'
          }
          positive={premium_delta != null && premium_delta < 0}
        />
        <SummaryCard
          label="Coverage Change"
          value={
            coverage_delta != null
              ? `${coverage_delta >= 0 ? '+' : ''}₹${Math.abs(coverage_delta / 100000).toFixed(1)}L`
              : '—'
          }
          positive={coverage_delta != null && coverage_delta > 0}
        />
      </div>

      {/* Recommendation */}
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
        <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-blue-800">
          {cost_effective ? (
            <CheckCircle className="h-4 w-4 text-blue-600" />
          ) : (
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          )}
          AI Recommendation
        </div>
        <p className="text-sm text-blue-900">{recommendation}</p>
      </div>

      {/* Waiting period risk */}
      {waiting_period_risk && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
          <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-amber-800">
            <AlertTriangle className="h-4 w-4" />
            Waiting Period Risk
          </div>
          <p className="text-sm text-amber-900">{waiting_period_risk}</p>
        </div>
      )}

      {/* Diffs table */}
      {diffs.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3 text-left">Benefit</th>
                <th className="px-4 py-3 text-left">Old Policy</th>
                <th className="px-4 py-3 text-left">New Policy</th>
                <th className="px-4 py-3 text-center">Change</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {diffs.map((diff, i) => (
                <tr key={i} className={CHANGE_ROW_BG[diff.change_type]}>
                  <td className="px-4 py-3 font-medium text-slate-700">
                    {diff.field.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                    {diff.notes && (
                      <p className="mt-0.5 text-xs font-normal text-slate-500">{diff.notes}</p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{formatValue(diff.old_value, diff.field)}</td>
                  <td className="px-4 py-3 text-slate-600">{formatValue(diff.new_value, diff.field)}</td>
                  <td className="px-4 py-3 text-center">
                    {CHANGE_ICONS[diff.change_type] ?? CHANGE_ICONS.unknown}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function SummaryCard({
  label,
  value,
  positive,
}: {
  label: string
  value: string
  positive: boolean
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p
        className={`mt-1 text-xl font-bold ${positive ? 'text-green-600' : 'text-red-600'}`}
      >
        {value}
      </p>
    </div>
  )
}
