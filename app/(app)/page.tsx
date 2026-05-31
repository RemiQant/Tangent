'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { PlaylistInput } from '@/components/ui/PlaylistInput'
import { GenerateButton } from '@/components/ui/GenerateButton'
import { PlaylistCard } from '@/components/ui/PlaylistCard'
import { SkeletonCard } from '@/components/ui/SkeletonCard'
import { AtmosphericOrb } from '@/components/ui/AtmosphericOrb'
import { TextGradient } from '@/components/ui/TextGradient'
import { useMotion } from '@/components/providers/MotionProvider'
import { mockPlaylists } from '@/lib/mock-data'
import type { Playlist } from '@/lib/types'

function isValidSpotifyUrl(url: string): boolean {
  return url.includes('open.spotify.com/playlist/')
}

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.05 } },
}

const itemVariants = {
  hidden:  { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' as const } },
}

export default function GeneratorPage() {
  const { shouldAnimate } = useMotion()
  const [url, setUrl]           = useState('')
  const [error, setError]       = useState<string | null>(null)
  const [isLoading, setLoading] = useState(false)
  const [playlists, setPlaylists] = useState<Playlist[]>(mockPlaylists.slice(0, 3))

  function handleGenerate() {
    if (!isValidSpotifyUrl(url)) {
      setError('Please paste a valid Spotify playlist URL.')
      return
    }
    setError(null)
    setLoading(true)
    setTimeout(() => setLoading(false), 2000)
  }

  function handleToggleFavorite(id: string) {
    setPlaylists((prev) =>
      prev.map((p) => p.id === id ? { ...p, isFavorite: !p.isFavorite } : p)
    )
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
            Extend Your <TextGradient>Sound</TextGradient>
          </h1>
          <p className="text-body-lg text-on-surface-variant max-w-xl">
            Paste any Spotify playlist link. Our AI engine will analyze the acoustic profile
            and curate a seamless extension of new, undiscovered tracks.
          </p>
        </div>

        <div className="w-full flex flex-col items-center gap-md">
          <PlaylistInput value={url} onChange={setUrl} error={error} />
          <GenerateButton isLoading={isLoading} onClick={handleGenerate} />
        </div>
      </section>

      <section className="relative z-10 max-w-3xl mx-auto mt-xxl">
        <h2 className="text-label-lg text-on-surface-variant mb-md uppercase tracking-widest">
          Recent Activity
        </h2>
        {isLoading ? (
          <div className="flex flex-col gap-md">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        ) : (
          <motion.div
            variants={shouldAnimate ? containerVariants : undefined}
            initial="hidden"
            animate="visible"
            className="flex flex-col gap-md"
          >
            {playlists.map((playlist) => (
              <motion.div key={playlist.id} variants={shouldAnimate ? itemVariants : undefined}>
                <PlaylistCard playlist={playlist} onToggleFavorite={handleToggleFavorite} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </section>
    </motion.div>
  )
}
