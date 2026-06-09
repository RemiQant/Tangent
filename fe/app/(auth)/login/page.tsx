'use client'

import { getLoginUrl } from '@/lib/auth'
import { GlassPanel } from '@/components/ui/GlassPanel'

export default function LoginPage() {
  const handleLogin = () => {
    window.location.href = getLoginUrl()
  }

  return (
    <GlassPanel className="w-full max-w-sm mx-4 p-8 flex flex-col items-center gap-6">
      <div className="flex flex-col items-center gap-2 text-center">
        <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mb-2">
          <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
        </div>
        <h1 className="text-title-lg text-on-surface font-semibold">Tangent</h1>
        <p className="text-body-lg text-on-surface-variant">AI-powered music recommendations</p>
      </div>

      <div className="w-full h-px bg-outline-variant" />

      <div className="flex flex-col items-center gap-3 w-full">
        <p className="text-sm text-on-surface-variant text-center">
          Connect your Spotify account to get personalized recommendations
        </p>
        <button
          onClick={handleLogin}
          className="w-full py-3 px-6 rounded-lg bg-primary text-on-primary font-medium text-body-lg hover:bg-primary/90 transition-colors shadow-glow-primary"
        >
          Connect with Spotify
        </button>
      </div>
    </GlassPanel>
  )
}
