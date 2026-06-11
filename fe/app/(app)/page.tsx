'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Info } from 'lucide-react'
import { SongSearchInput } from '@/components/ui/SongSearchInput'
import { SongRecommendationCard } from '@/components/ui/SongRecommendationCard'
import { Toast } from '@/components/ui/Toast'
import { SkeletonCard } from '@/components/ui/SkeletonCard'
import { AtmosphericOrb } from '@/components/ui/AtmosphericOrb'
import { TextGradient } from '@/components/ui/TextGradient'
import { useMotion } from '@/components/providers/MotionProvider'
import api from '@/lib/api'
import type { SongResult, SongRecommendation } from '@/lib/types'

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.05 } },
}
const itemVariants = {
  hidden:  { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' as const } },
}

interface ToastState {
  message: string
  type: 'success' | 'error'
}

export default function GeneratorPage() {
  const { shouldAnimate } = useMotion()
  const [selectedSong, setSelectedSong] = useState<SongResult | null>(null)
  const [recommendations, setRecommendations] = useState<SongRecommendation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [toast, setToast] = useState<ToastState | null>(null)
  const [genreFiltered, setGenreFiltered] = useState(true)

  const showToast = useCallback((message: string, type: 'success' | 'error') => {
    setToast({ message, type })
  }, [])

  async function handleGenerate() {
    if (!selectedSong) return
    setIsLoading(true)
    setRecommendations([])

    try {
      const result = await api.recommendations.getSongs(selectedSong.song_id)
      setRecommendations(result.recommendations)
      setGenreFiltered(result.genre_filtered)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Something went wrong'
      if (msg.includes('Not enough')) {
        showToast('Not enough similar songs found. Try a different track.', 'error')
      } else if (msg.includes('Too many')) {
        showToast('Too many requests. Wait a moment and try again.', 'error')
      } else {
        showToast(msg || 'Connection error. Check your internet and try again.', 'error')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={shouldAnimate ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="relative min-h-dvh px-margin-mobile md:px-margin-desktop pb-xl"
    >
      <AtmosphericOrb color="secondary" size="lg" position="top-left" />
      <AtmosphericOrb color="primary"   size="md" position="bottom-right" />

      <section className="relative z-10 max-w-3xl mx-auto pt-xl text-center flex flex-col items-center gap-xl">
        <div>
          <h1 className="text-headline-xl font-bold text-on-surface mb-sm">
            Discover Your <TextGradient>Sound</TextGradient>
          </h1>
          <p className="text-body-lg text-on-surface-variant max-w-xl">
            Search for a song. Our AI engine will find acoustically similar tracks you&apos;ll love.
          </p>
        </div>

        <div className="w-full flex flex-col items-center gap-md">
          <div className="w-full max-w-lg">
            <SongSearchInput
              onSelect={setSelectedSong}
              selectedSong={selectedSong}
              onClear={() => { setSelectedSong(null); setRecommendations([]) }}
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={!selectedSong || isLoading}
            className="flex items-center gap-sm bg-primary text-on-primary font-semibold rounded-xl px-8 py-4 transition-all duration-150 hover:scale-[1.02] hover:shadow-glow-primary-lg disabled:opacity-70 disabled:scale-100 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 rounded-full border-2 border-on-primary border-t-transparent animate-spin" />
                <span>Finding Similar Songs…</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" aria-hidden="true" />
                <span>Find Similar Songs</span>
              </>
            )}
          </button>
        </div>
      </section>

      {(isLoading || recommendations.length > 0) && (
        <section className="relative z-10 mt-xxl">
          <h2 className="text-label-lg text-on-surface-variant mb-md uppercase tracking-widest">
            {isLoading ? 'Searching…' : `${recommendations.length} Recommendations`}
          </h2>

          {!isLoading && recommendations.length > 0 && !genreFiltered && (
            <p className="flex items-center gap-2 text-body-sm text-on-surface-variant mb-md">
              <Info className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              Showing audio-similarity matches — genre info unavailable for this song.
            </p>
          )}

          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-md">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : (
            <motion.div
              variants={shouldAnimate ? containerVariants : undefined}
              initial="hidden"
              animate="visible"
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-md"
            >
              {recommendations.map((song) => (
                <motion.div key={song.song_id} variants={shouldAnimate ? itemVariants : undefined} className="h-full">
                  <SongRecommendationCard song={song} />
                </motion.div>
              ))}
            </motion.div>
          )}
        </section>
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onDismiss={() => setToast(null)}
        />
      )}
    </motion.div>
  )
}
