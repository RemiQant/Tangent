import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import HistoryPage from '@/app/(app)/history/page'

vi.mock('next/navigation', () => ({ usePathname: () => '/history' }))
vi.mock('next/image', () => ({ default: (props: any) => <img {...props} /> }))
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  useReducedMotion: () => false,
}))

describe('Generation History', () => {
  it('renders page heading', () => {
    render(<HistoryPage />)
    expect(screen.getByRole('heading', { name: /generation history/i })).toBeInTheDocument()
  })

  it('renders search input', () => {
    render(<HistoryPage />)
    expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument()
  })

  it('shows empty state when no history exists', () => {
    render(<HistoryPage />)
    expect(screen.getByText(/no generation history yet/i)).toBeInTheDocument()
  })

  it('shows session count', () => {
    render(<HistoryPage />)
    expect(screen.getByText(/0 sessions/i)).toBeInTheDocument()
  })
})
