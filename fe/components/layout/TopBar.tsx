'use client'

import { useState, useRef, useEffect } from 'react'
import { Music2, LogOut, ChevronDown, User } from 'lucide-react'
import { TextGradient } from '@/components/ui/TextGradient'
import { clearToken, getDisplayName } from '@/lib/auth'
import { useRouter } from 'next/navigation'

export function TopBar() {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [username, setUsername] = useState<string | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setUsername(getDisplayName())
  }, [])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  function handleLogout() {
    clearToken()
    router.replace('/login')
  }

  const initials = username
    ? username.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()
    : null

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 h-14 bg-surface-dim/90 backdrop-blur-md border-b border-white/10">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center">
          <Music2 className="w-4 h-4 text-primary" aria-hidden="true" />
        </div>
        <div className="leading-none">
          <TextGradient as="span" className="text-base font-bold">
            Tangent
          </TextGradient>
          <p className="text-xs text-on-surface-variant mt-0.5">AI Playlist Engine</p>
        </div>
      </div>

      {/* Profile dropdown */}
      <div ref={dropdownRef} className="relative">
        <button
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-haspopup="true"
          className="flex items-center gap-2 pl-1 pr-3 py-1 rounded-full bg-surface-container border border-white/10 hover:border-primary/40 transition-colors"
        >
          <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
            {initials ? (
              <span className="text-xs font-semibold text-primary">{initials}</span>
            ) : (
              <User className="w-3.5 h-3.5 text-primary" aria-hidden="true" />
            )}
          </div>
          {username && (
            <span className="text-sm text-on-surface hidden sm:block max-w-[120px] truncate">
              {username}
            </span>
          )}
          <ChevronDown
            className={`w-3.5 h-3.5 text-on-surface-variant transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
            aria-hidden="true"
          />
        </button>

        {open && (
          <div className="absolute right-0 mt-2 w-52 rounded-xl bg-surface-container border border-white/10 shadow-2xl overflow-hidden">
            {username && (
              <>
                <div className="flex items-center gap-3 px-4 py-3">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-semibold text-primary">{initials}</span>
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs text-on-surface-variant">Signed in as</p>
                    <p className="text-sm font-medium text-on-surface truncate">{username}</p>
                  </div>
                </div>
                <div className="h-px bg-white/10" />
              </>
            )}
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm text-on-surface hover:bg-surface-container-high transition-colors"
            >
              <LogOut className="w-4 h-4 text-on-surface-variant" aria-hidden="true" />
              Log out
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
