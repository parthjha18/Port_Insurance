import { useState } from 'react'
import { chatWithPolicy, type ChatMessage } from '../api/client'

export interface UseChatResult {
  messages: ChatMessage[]
  loading: boolean
  error: string | null
  send: (userMessage: string) => Promise<void>
  clear: () => void
}

export function useChat(collectionId: string, personaId?: string): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const send = async (userMessage: string) => {
    if (!userMessage.trim() || loading) return

    const newMessages: ChatMessage[] = [
      ...messages,
      { role: 'user', content: userMessage },
    ]
    setMessages(newMessages)
    setLoading(true)
    setError(null)

    try {
      const res = await chatWithPolicy(collectionId, newMessages, personaId)
      setMessages([...newMessages, { role: 'assistant', content: res.answer }])
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Chat failed. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const clear = () => {
    setMessages([])
    setError(null)
  }

  return { messages, loading, error, send, clear }
}
