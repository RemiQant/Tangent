'use client'

import { useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { setToken } from '@/lib/auth'

function AuthCallbackInner() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      setToken(token)
    }
    router.replace('/')
  }, [searchParams, router])

  return (
    <div className="min-h-dvh bg-background flex items-center justify-center">
      <p className="text-on-surface-variant text-body-lg">Signing you in…</p>
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-dvh bg-background flex items-center justify-center">
        <p className="text-on-surface-variant text-body-lg">Loading…</p>
      </div>
    }>
      <AuthCallbackInner />
    </Suspense>
  )
}
