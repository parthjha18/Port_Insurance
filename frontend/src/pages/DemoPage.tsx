import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, ArrowRight } from 'lucide-react'
import { PersonaSelector } from '../components/PersonaSelector'
import { ChatInterface } from '../components/ChatInterface'
import { useChat } from '../hooks/useChat'
import type { Persona } from '../api/client'

const DEMO_COLLECTION_ID = 'demo-mode-no-collection'

export function DemoPage() {
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null)
  const [demoStarted, setDemoStarted] = useState(false)
  const navigate = useNavigate()

  const chat = useChat(DEMO_COLLECTION_ID, selectedPersona?.id)

  const startDemo = () => {
    if (!selectedPersona) return
    setDemoStarted(true)
    setTimeout(() => {
      chat.send(selectedPersona.demo_scenario)
    }, 200)
  }

  return (
    <div className="mx-auto max-w-5xl space-y-8 px-4 py-10">
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 shadow-lg">
          <Sparkles className="h-7 w-7 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-slate-800">Demo Mode</h1>
        <p className="mt-2 text-slate-500">
          Explore how the assistant advises real Indian professionals on health insurance porting.
          Personas are sourced from the LinkedIn India dataset.
        </p>
      </div>

      {!demoStarted ? (
        <div className="space-y-6">
          <PersonaSelector selected={selectedPersona} onSelect={setSelectedPersona} />

          {selectedPersona && (
            <div className="flex justify-center">
              <button
                onClick={startDemo}
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-500 to-blue-500 px-8 py-3 font-semibold text-white shadow-md transition hover:opacity-90"
              >
                Start Demo
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="rounded-full bg-purple-100 px-3 py-1 text-sm font-medium text-purple-700">
              Demo: {selectedPersona?.full_name}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setDemoStarted(false)
                  chat.clear()
                }}
                className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-50"
              >
                Change Persona
              </button>
              <button
                onClick={() => navigate('/upload')}
                className="rounded-lg bg-blue-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-600"
              >
                Use Your Own Policy
              </button>
            </div>
          </div>

          <div className="h-[28rem]">
            <ChatInterface
              chat={chat}
              placeholder="Ask a follow-up question about this scenario…"
            />
          </div>
        </div>
      )}
    </div>
  )
}
