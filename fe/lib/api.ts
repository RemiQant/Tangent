import type { SongResult, RecommendationResponse } from '@/lib/types'
import { getToken, clearToken } from '@/lib/auth'

function getBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8080'
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> ?? {}),
  }

  const baseUrl = getBaseUrl().replace(/\/$/, '') // Remove trailing slash if present
  const cleanPath = path.replace(/^\//, '')      // Remove leading slash from the path if present
  const fullUrl = `${baseUrl}/${cleanPath}`
  
  const response = await fetch(`${getBaseUrl()}${path}`, { ...options, headers })

  if (response.status === 401) {
    clearToken()
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(detail.detail ?? `Request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

const api = {
  search: {
    songs(q: string, limit = 5): Promise<SongResult[]> {
      const params = new URLSearchParams({ q, limit: String(limit) })
      return request<SongResult[]>(`/api/v1/search/songs?${params}`)
    },
  },
  recommendations: {
    getSongs(songId: string, maxDistance = 0.5): Promise<RecommendationResponse> {
      return request<RecommendationResponse>('/api/v1/recommendations/songs', {
        method: 'POST',
        body: JSON.stringify({ song_id: songId, max_distance: maxDistance }),
      })
    },
  },
}

export default api
