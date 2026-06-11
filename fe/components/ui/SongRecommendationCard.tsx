import { Music } from 'lucide-react'
import { GlassPanel } from '@/components/ui/GlassPanel'
import type { SongRecommendation } from '@/lib/types'

interface FeatureBarProps {
  label: string
  value: number
  color: string
}

function FeatureBar({ label, value, color }: FeatureBarProps) {
  const pct = Math.round(value * 100)
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <span className="text-xs text-on-surface-variant">{label}</span>
        <span className="text-xs text-on-surface-variant">{pct}%</span>
      </div>
      <div className="h-1 rounded-full bg-surface-container-highest overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}

interface GenreBadgeProps {
  family: string
}

function GenreBadge({ family }: GenreBadgeProps) {
  return (
    <span className="text-xs px-2 py-0.5 rounded-full bg-surface-container-highest text-on-surface-variant">
      {family}
    </span>
  )
}

interface SongRecommendationCardProps {
  song: SongRecommendation
}

export function SongRecommendationCard({ song }: SongRecommendationCardProps) {
  const matchScore = Math.round((1 - song.distance_score) * 100)

  const matchColor =
    matchScore >= 80 ? 'text-primary' :
    matchScore >= 60 ? 'text-secondary' :
    'text-on-surface-variant'

  return (
    <GlassPanel className="p-4 flex flex-col gap-4 h-full">
      <div className="flex items-start gap-3">
        <div className="w-12 h-12 rounded flex-shrink-0 bg-surface-container-high flex items-center justify-center">
          <Music className="w-6 h-6 text-on-surface-variant" aria-hidden="true" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-on-surface truncate" title={song.name}>
            {song.name}
          </p>
          <p className="text-xs text-on-surface-variant truncate">{song.artists}</p>
        </div>

        <div className="flex-shrink-0 text-right">
          <span
            className={`text-title-md font-semibold ${matchColor}`}
            aria-label={`Match score: ${matchScore}%`}
          >
            {matchScore}%
          </span>
          <p className="text-xs text-on-surface-variant">match</p>
        </div>
      </div>

      {song.genre_families.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {song.genre_families.slice(0, 3).map((family) => (
            <GenreBadge key={family} family={family} />
          ))}
        </div>
      )}

      <div className="flex flex-col gap-2 flex-1">
        <FeatureBar label="Energy" value={song.energy} color="#53e076" />
        <FeatureBar label="Dance"  value={song.danceability} color="#d1bcff" />
        <FeatureBar label="Valence" value={song.valence} color="#7ec8e3" />
      </div>
    </GlassPanel>
  )
}
