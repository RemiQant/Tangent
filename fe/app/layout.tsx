import type { Metadata } from 'next'
import { MotionProvider } from '@/components/providers/MotionProvider'
import '@/app/globals.css'

export const metadata: Metadata = {
  title: 'Tangent — AI Playlist Engine',
  description: 'Extend your Spotify playlists with AI-curated tracks',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-background text-on-surface antialiased">
        <MotionProvider>
          {children}
        </MotionProvider>
      </body>
    </html>
  )
}
