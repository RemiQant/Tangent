import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { SongSearchInput } from '@/components/ui/SongSearchInput'
import type { SongResult } from '@/lib/types'

const mockSong: SongResult = {
  song_id: '4iV5W9uYEdYUVa79Axb7Rh',
  name: 'Neon',
  artists: 'John Mayer',
  album_art_url: 'https://example.com/img.jpg',
}

// vi.hoisted runs before vi.mock hoisting, so variables defined here
// are safe to reference inside the vi.mock factory.
const { mockSearchSongs } = vi.hoisted(() => ({
  mockSearchSongs: vi.fn(),
}))

vi.mock('@/lib/api', () => ({
  default: {
    search: {
      songs: mockSearchSongs,
    },
  },
}))

beforeEach(() => {
  mockSearchSongs.mockResolvedValue([mockSong])
  vi.useFakeTimers()
})

afterEach(() => {
  vi.runOnlyPendingTimers()
  vi.useRealTimers()
})

describe('SongSearchInput', () => {
  it('renders search input', () => {
    render(<SongSearchInput onSelect={vi.fn()} />)
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('shows selected song chip when selectedSong is provided', () => {
    render(<SongSearchInput onSelect={vi.fn()} selectedSong={mockSong} />)
    expect(screen.getByText('Neon')).toBeInTheDocument()
    expect(screen.getByText('John Mayer')).toBeInTheDocument()
    expect(screen.getByLabelText('Clear selected song')).toBeInTheDocument()
  })

  it('calls onClear when clear button is clicked on selected song', () => {
    const onClear = vi.fn()
    render(<SongSearchInput onSelect={vi.fn()} selectedSong={mockSong} onClear={onClear} />)
    fireEvent.click(screen.getByLabelText('Clear selected song'))
    expect(onClear).toHaveBeenCalled()
  })

  it('calls onSelect when a search result is clicked', async () => {
    const onSelect = vi.fn()
    render(<SongSearchInput onSelect={onSelect} />)
    const input = screen.getByRole('combobox')
    fireEvent.change(input, { target: { value: 'Neon' } })
    // Advance fake timers past the 300ms debounce delay, then flush all
    // pending microtasks (Promise callbacks from the API call) so the
    // component state update lands before we query the DOM.
    await act(async () => {
      vi.advanceTimersByTime(300)
      // Yield to let the resolved Promise callbacks run inside act()
      await Promise.resolve()
    })
    expect(screen.getByText('Neon')).toBeInTheDocument()
    fireEvent.click(screen.getByText('Neon'))
    expect(onSelect).toHaveBeenCalledWith(mockSong)
  })
})
