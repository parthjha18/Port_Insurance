import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { Shield, Upload, GitCompare, MessageSquare, Sparkles } from 'lucide-react'
import { UploadPage } from './pages/UploadPage'
import { ComparePage } from './pages/ComparePage'
import { ChatPage } from './pages/ChatPage'
import { DemoPage } from './pages/DemoPage'

const NAV_LINKS = [
  { to: '/upload', label: 'Upload', icon: Upload },
  { to: '/compare', label: 'Compare', icon: GitCompare },
  { to: '/chat', label: 'Chat', icon: MessageSquare },
  { to: '/demo', label: 'Demo', icon: Sparkles },
]

function Navbar() {
  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <NavLink to="/upload" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-500">
            <Shield className="h-4 w-4 text-white" />
          </div>
          <span className="text-sm font-bold text-slate-800">InsurePort AI</span>
        </NavLink>

        <div className="flex items-center gap-1">
          {NAV_LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition
                ${isActive ? 'bg-blue-50 text-blue-600' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'}`
              }
            >
              <Icon className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">{label}</span>
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/demo" element={<DemoPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
