const TOKEN_KEY = 'tangent_jwt'

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(jwt: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(TOKEN_KEY, jwt)
}

export function clearToken(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(TOKEN_KEY)
}

export function isAuthenticated(): boolean {
  return getToken() !== null
}

export function getLoginUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8080'
  return `${apiUrl}/api/v1/auth/login`
}

export function getDisplayName(): string | null {
  const token = getToken()
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return (payload.name as string) ?? null
  } catch {
    return null
  }
}
