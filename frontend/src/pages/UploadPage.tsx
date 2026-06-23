import { useNavigate } from 'react-router-dom'
import { ArrowRight, Shield } from 'lucide-react'
import { DocumentUpload } from '../components/DocumentUpload'
import { useUpload } from '../hooks/useUpload'

export function UploadPage() {
  const oldPolicy = useUpload()
  const newPolicy = useUpload()
  const navigate = useNavigate()

  const canCompare =
    oldPolicy.stage === 'done' &&
    newPolicy.stage === 'done' &&
    oldPolicy.uploadResponse &&
    newPolicy.uploadResponse

  const handleCompare = () => {
    if (!oldPolicy.uploadResponse || !newPolicy.uploadResponse) return
    navigate('/compare', {
      state: {
        oldCollectionId: oldPolicy.uploadResponse.collection_id,
        newCollectionId: newPolicy.uploadResponse.collection_id,
      },
    })
  }

  const canChat =
    oldPolicy.stage === 'done' && oldPolicy.uploadResponse

  const handleChat = () => {
    if (!oldPolicy.uploadResponse) return
    navigate('/chat', {
      state: { collectionId: oldPolicy.uploadResponse.collection_id },
    })
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-10">
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500 shadow-lg">
          <Shield className="h-7 w-7 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-slate-800">Insurance Port Assistant</h1>
        <p className="mt-2 text-slate-500">
          Upload your policy documents. We'll extract benefits, compare them, and tell you if
          porting makes sense.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <DocumentUpload label="Your Current Policy (Old Insurer)" result={oldPolicy} />
        <DocumentUpload label="Target Policy (New Insurer) — Optional" result={newPolicy} />
      </div>

      <div className="flex flex-wrap justify-center gap-3">
        {canCompare && (
          <button
            onClick={handleCompare}
            className="flex items-center gap-2 rounded-xl bg-blue-500 px-6 py-3 font-semibold text-white shadow-md transition hover:bg-blue-600"
          >
            Compare Policies
            <ArrowRight className="h-4 w-4" />
          </button>
        )}
        {canChat && (
          <button
            onClick={handleChat}
            className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3 font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
          >
            Chat with Policy
            <ArrowRight className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}
