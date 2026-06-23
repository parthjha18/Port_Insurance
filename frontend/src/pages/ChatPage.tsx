import { useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, MessageSquare } from 'lucide-react'
import { ChatInterface } from '../components/ChatInterface'
import { useChat } from '../hooks/useChat'

interface LocationState {
  collectionId: string
  personaId?: string
}

export function ChatPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null

  const chat = useChat(state?.collectionId ?? '', state?.personaId)

  if (!state?.collectionId) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <p className="text-slate-500">No policy loaded for chat.</p>
        <button
          onClick={() => navigate('/upload')}
          className="rounded-xl bg-blue-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-600"
        >
          Upload a Policy
        </button>
      </div>
    )
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-4rem)] max-w-3xl flex-col px-4 py-6">
      <div className="mb-4 flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1 rounded-lg px-2 py-1.5 text-sm text-slate-500 hover:bg-slate-100"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
        <div className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-blue-500" />
          <h1 className="text-xl font-bold text-slate-800">Chat with Your Policy</h1>
        </div>
      </div>

      <div className="min-h-0 flex-1">
        <ChatInterface chat={chat} />
      </div>
    </div>
  )
}
