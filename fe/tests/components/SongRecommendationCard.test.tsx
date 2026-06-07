import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { SongRecommendationCard } from '@/components/ui/SongRecommendationCard'
import type { SongRecommendation } from '@/lib/types'

const mockSong: SongRecommendation = {
  song_id: '4iV5W9uYEdYUVa79Axb7Rh',
  name: 'Neon',
  artists: 'John Mayer',
  distance_score: 0.2,
  danceability: 0.75,
  energy: 0.65,
  speechiness: 0.04,
  acousticness: 0.3,
  instrumentalness: 0.0,
  liveness: 0.1,
  valence: 0.8,
  tempo: 120,
}

describe('SongRecommendationCard', () => {
  it('renders song name and artist', () => {
    render(<SongRecommendationCard song={mockSong} onAddToPlaylist={vi.fn()} />)
    expect(screen.getByText('Neon')).toBeInTheDocument()
    expect(screen.getByText('John Mayer')).toBeInTheDocument()
  })

  it('shows correct match score (1 - distance_score) * 100', () => {
    render(<SongRecommendationCard song={mockSong} onAddToPlaylist={vi.fn()} />)
    // distance_score = 0.2 → match = 80%
    expect(screen.getByLabelText('Match score: 80%')).toBeInTheDocument()
  })

  it('shows feature bars for Energy, Dance, Valence', () => {
    render(<SongRecommendationCard song={mockSong} onAddToPlaylist={vi.fn()} />)
    expect(screen.getByText('Energy')).toBeInTheDocument()
    expect(screen.getByText('Dance')).toBeInTheDocument()
    expect(screen.getByText('Valence')).toBeInTheDocument()
  })

  it('calls onAddToPlaylist when button is clicked', () => {
    const onAdd = vi.fn()
    render(<SongRecommendationCard song={mockSong} onAddToPlaylist={onAdd} />)
    fireEvent.click(screen.getByRole('button', { name: /add neon to playlist/i }))
    expect(onAdd).toHaveBeenCalledWith(mockSong)
  })

  it('renders distance_score 0.0 as 100% match', () => {
    const perfectSong = { ...mockSong, distance_score: 0 }
    render(<SongRecommendationCard song={perfectSong} onAddToPlaylist={vi.fn()} />)
    expect(screen.getByLabelText('Match score: 100%')).toBeInTheDocument()
  })
})
