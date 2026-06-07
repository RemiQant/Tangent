import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import LoginPage from '@/app/(auth)/login/page'

vi.mock('@/lib/auth', () => ({
  getLoginUrl: () => 'http://localhost:8080/api/v1/auth/login',
}))

describe('LoginPage', () => {
  it('renders Connect with Spotify button', () => {
    render(<LoginPage />)
    expect(screen.getByRole('button', { name: /connect with spotify/i })).toBeInTheDocument()
  })

  it('shows app name', () => {
    render(<LoginPage />)
    expect(screen.getByText('Tangent')).toBeInTheDocument()
  })
})
