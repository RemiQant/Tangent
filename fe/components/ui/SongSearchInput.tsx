'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { Search, X, Music } from 'lucide-react'
import type { SongResult } from '@/lib/types'
import api from '@/lib/api'

interface SongSearchInputProps {
  onSelect: (song: SongResult) => void
  selectedSong?: SongResult | null
  onClear?: () => void
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(id)
  }, [value, delay])
  return debounced
}

export function SongSearchInput({ onSelect, selectedSong, onClear }: SongSearchInputProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SongResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const debouncedQuery = useDebounce(query, 300)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setResults([])
      setIsOpen(false)
      return
    }

    let cancelled = false
    setIsSearching(true)
    setError(null)

    api.search.songs(debouncedQuery).then((data) => {
      if (!cancelled) {
        setResults(data)
        setIsOpen(true)
        setIsSearching(false)
      }
    }).catch((err: Error) => {
      if (!cancelled) {
        setError(err.message)
        setIsSearching(false)
        setIsOpen(false)
      }
    })

    return () => { cancelled = true }
  }, [debouncedQuery])

  const handleSelect = useCallback((song: SongResult) => {
    onSelect(song)
    setQuery('')
    setIsOpen(false)
    setResults([])
  }, [onSelect])

  const handleClear = useCallback(() => {
    setQuery('')
    setResults([])
    setIsOpen(false)
    onClear?.()
  }, [onClear])

  if (selectedSong) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-lg bg-surface-container border border-outline-variant">
        <div className="w-10 h-10 rounded flex-shrink-0 bg-surface-container-high flex items-center justify-center overflow-hidden">
          {selectedSong.album_art_url ? (
            <img src={selectedSong.album_art_url} alt={selectedSong.name} className="w-full h-full object-cover" />
          ) : (
            <Music className="w-5 h-5 text-on-surface-variant" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-on-surface truncate">{selectedSong.name}</p>
          <p className="text-xs text-on-surface-variant truncate">{selectedSong.artists}</p>
        </div>
        <button
          onClick={handleClear}
          aria-label="Clear selected song"
          className="flex-shrink-0 p-1 rounded-full hover:bg-surface-container-high text-on-surface-variant transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    )
  }

  return (
    <div ref={containerRef} className="relative">
      <div className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-surface-container border border-outline-variant focus-within:border-primary transition-colors">
        <Search className="w-4 h-4 text-on-surface-variant flex-shrink-0" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          placeholder="Search for a song…"
          className="flex-1 bg-transparent text-on-surface text-sm placeholder:text-on-surface-variant outline-none"
          aria-label="Search songs"
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          role="combobox"
          aria-autocomplete="list"
        />
        {isSearching && (
          <div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin flex-shrink-0" aria-label="Searching" />
        )}
        {query && !isSearching && (
          <button onClick={() => setQuery('')} aria-label="Clear search" className="flex-shrink-0 text-on-surface-variant hover:text-on-surface transition-colors">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {error && (
        <p className="mt-1 text-xs text-error">{error}</p>
      )}

      {isOpen && results.length > 0 && (
        <ul
          role="listbox"
          className="absolute z-50 w-full mt-1 rounded-lg bg-surface-container border border-outline-variant shadow-lg overflow-hidden"
        >
          {results.map((song) => (
            <li key={song.song_id} role="option" aria-selected={false}>
              <button
                onClick={() => handleSelect(song)}
                className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-surface-container-high transition-colors text-left"
              >
                <div className="w-10 h-10 rounded flex-shrink-0 bg-surface-container-highest flex items-center justify-center overflow-hidden">
                  {song.album_art_url ? (
                    <img src={song.album_art_url} alt={song.name} className="w-full h-full object-cover" />
                  ) : (
                    <Music className="w-5 h-5 text-on-surface-variant" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-on-surface truncate">{song.name}</p>
                  <p className="text-xs text-on-surface-variant truncate">{song.artists}</p>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}

      {isOpen && results.length === 0 && !isSearching && debouncedQuery && (
        <div className="absolute z-50 w-full mt-1 rounded-lg bg-surface-container border border-outline-variant p-4 text-center">
          <p className="text-sm text-on-surface-variant">No songs found</p>
        </div>
      )}
    </div>
  )
}
