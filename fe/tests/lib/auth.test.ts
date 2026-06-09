import { describe, it, expect, beforeEach, vi } from 'vitest'

beforeEach(() => {
  localStorage.clear()
  vi.unstubAllEnvs()
  vi.resetModules()
})

describe('auth helpers', () => {
  it('getToken returns null when nothing stored', async () => {
    const { getToken } = await import('@/lib/auth')
    expect(getToken()).toBeNull()
  })

  it('setToken stores value in localStorage', async () => {
    const { setToken, getToken } = await import('@/lib/auth')
    setToken('test.jwt.token')
    expect(getToken()).toBe('test.jwt.token')
  })

  it('clearToken removes value from localStorage', async () => {
    const { setToken, clearToken, getToken } = await import('@/lib/auth')
    setToken('test.jwt.token')
    clearToken()
    expect(getToken()).toBeNull()
  })

  it('isAuthenticated returns false when no token', async () => {
    const { isAuthenticated } = await import('@/lib/auth')
    expect(isAuthenticated()).toBe(false)
  })

  it('isAuthenticated returns true when token set', async () => {
    const { setToken, isAuthenticated } = await import('@/lib/auth')
    setToken('test.jwt.token')
    expect(isAuthenticated()).toBe(true)
  })

  it('getLoginUrl uses NEXT_PUBLIC_API_URL env var', async () => {
    vi.stubEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8080')
    const { getLoginUrl } = await import('@/lib/auth')
    expect(getLoginUrl()).toContain('/api/v1/auth/login')
  })
})
