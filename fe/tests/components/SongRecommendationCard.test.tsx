import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
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
  genres: ['pop', 'singer-songwriter'],
  genre_families: ['Pop', 'Folk/Acoustic'],
}

describe('SongRecommendationCard', () => {
  it('renders song name and artist', () => {
    render(<SongRecommendationCard song={mockSong} />)
    expect(screen.getByText('Neon')).toBeInTheDocument()
    expect(screen.getByText('John Mayer')).toBeInTheDocument()
  })

  it('shows correct match score (1 - distance_score) * 100', () => {
    render(<SongRecommendationCard song={mockSong} />)
    // distance_score = 0.2 → match = 80%
    expect(screen.getByLabelText('Match score: 80%')).toBeInTheDocument()
  })

  it('shows feature bars for Energy, Dance, Valence', () => {
    render(<SongRecommendationCard song={mockSong} />)
    expect(screen.getByText('Energy')).toBeInTheDocument()
    expect(screen.getByText('Dance')).toBeInTheDocument()
    expect(screen.getByText('Valence')).toBeInTheDocument()
  })

  it('renders distance_score 0.0 as 100% match', () => {
    const perfectSong = { ...mockSong, distance_score: 0 }
    render(<SongRecommendationCard song={perfectSong} />)
    expect(screen.getByLabelText('Match score: 100%')).toBeInTheDocument()
  })

  it('renders genre family badges', () => {
    render(<SongRecommendationCard song={mockSong} />)
    expect(screen.getByText('Pop')).toBeInTheDocument()
    expect(screen.getByText('Folk/Acoustic')).toBeInTheDocument()
  })

  it('renders no genre badges when genre_families is empty', () => {
    const unfilteredSong = { ...mockSong, genres: [], genre_families: [] }
    render(<SongRecommendationCard song={unfilteredSong} />)
    expect(screen.queryByText('Pop')).not.toBeInTheDocument()
    expect(screen.queryByText('Folk/Acoustic')).not.toBeInTheDocument()
  })

  it('limits genre badges to 3', () => {
    const multiGenreSong = { ...mockSong, genre_families: ['EDM', 'Pop', 'Rock', 'Industrial'] }
    render(<SongRecommendationCard song={multiGenreSong} />)
    expect(screen.getByText('EDM')).toBeInTheDocument()
    expect(screen.getByText('Pop')).toBeInTheDocument()
    expect(screen.getByText('Rock')).toBeInTheDocument()
    expect(screen.queryByText('Industrial')).not.toBeInTheDocument()
  })
})
