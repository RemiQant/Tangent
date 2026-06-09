export interface Playlist {
  id: string
  title: string
  thumbnailUrl: string
  trackCount: number
  extendedBy: number
  createdAt: string
  status: 'completed' | 'processing' | 'failed'
  isFavorite: boolean
  spotifyUrl: string
  acousticProfile?: AcousticProfile
}

export interface AcousticProfile {
  energy: number      // 0–100
  danceability: number
  valence: number
  acousticness: number
}

export interface Track {
  id: string
  title: string
  artist: string
  matchConfidence: number  // 0–100
  bpm: number
  key: string
  albumArt: string
  spotifyUrl: string
}

export interface StatMetric {
  id: string
  label: string
  value: string | number
  trend?: string
  trendPositive?: boolean
  icon: string
}

export interface WeeklyDiscovery {
  week: string
  tracks: number
}

export interface GenerationResult {
  playlist: Playlist
  tracks: Track[]
}

export interface SongResult {
  song_id: string
  name: string
  artists: string
  album_art_url: string
}

export interface SongRecommendation {
  song_id: string
  name: string
  artists: string
  distance_score: number
  danceability: number
  energy: number
  speechiness: number
  acousticness: number
  instrumentalness: number
  liveness: number
  valence: number
  tempo: number
}

export interface RecommendationResponse {
  seed_song_id: string
  total_recommendations: number
  recommendations: SongRecommendation[]
}
