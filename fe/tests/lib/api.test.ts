import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'

beforeEach(() => {
  localStorage.clear()
  vi.restoreAllMocks()
  vi.resetModules()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('api client', () => {
  it('search.songs calls correct endpoint', async () => {
    localStorage.setItem('tangent_jwt', 'test.jwt')
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ song_id: 'abc', name: 'Song', artists: 'Artist', album_art_url: '' }],
    })
    vi.stubGlobal('fetch', mockFetch)

    const api = (await import('@/lib/api')).default
    const result = await api.search.songs('Neon')

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/search/songs'),
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: 'Bearer test.jwt' }) })
    )
    expect(result[0].song_id).toBe('abc')
  })

  it('recommendations.getSongs calls POST endpoint', async () => {
    localStorage.setItem('tangent_jwt', 'test.jwt')
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ seed_song_id: 'abc', total_recommendations: 1, recommendations: [] }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const api = (await import('@/lib/api')).default
    await api.recommendations.getSongs('abc')

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/recommendations/songs'),
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('playlists.export calls POST endpoint', async () => {
    localStorage.setItem('tangent_jwt', 'test.jwt')
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ message: 'ok', playlist_id: 'p1', spotify_url: 'https://open.spotify.com/playlist/p1' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const api = (await import('@/lib/api')).default
    const result = await api.playlists.export('My Playlist', ['track1'])

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/playlists/export'),
      expect.objectContaining({ method: 'POST' })
    )
    expect(result.playlist_id).toBe('p1')
  })

  it('clears token and throws on 401', async () => {
    localStorage.setItem('tangent_jwt', 'expired.jwt')
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' }),
    })
    vi.stubGlobal('fetch', mockFetch)
    vi.stubGlobal('window', { location: { href: '' } })

    const api = (await import('@/lib/api')).default
    await expect(api.search.songs('test')).rejects.toThrow('Unauthorized')
    expect(localStorage.getItem('tangent_jwt')).toBeNull()
  })
})
