import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import GeneratorPage from '@/app/(app)/page'

vi.mock('next/navigation', () => ({ usePathname: () => '/' }))
vi.mock('next/image', () => ({ default: (props: any) => <img {...props} /> }))
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  useReducedMotion: () => false,
}))

describe('Generator Dashboard', () => {
  it('renders headline', () => {
    render(<GeneratorPage />)
    expect(screen.getByRole('heading', { name: /discover your sound/i })).toBeInTheDocument()
  })

  it('renders song search input', () => {
    render(<GeneratorPage />)
    expect(screen.getByRole('combobox', { name: /search songs/i })).toBeInTheDocument()
  })

  it('renders find similar songs button', () => {
    render(<GeneratorPage />)
    expect(screen.getByRole('button', { name: /find similar songs/i })).toBeInTheDocument()
  })

  it('button is disabled when no song is selected', () => {
    render(<GeneratorPage />)
    expect(screen.getByRole('button', { name: /find similar songs/i })).toBeDisabled()
  })
})
