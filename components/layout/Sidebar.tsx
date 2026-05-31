'use client'

import { usePathname } from 'next/navigation'
import { NavItem } from './NavItem'
import { TextGradient } from '@/components/ui/TextGradient'
import { Music2 } from 'lucide-react'

const navItems = [
  { href: '/',          icon: 'sparkles' as const, label: 'Generator' },
  { href: '/history',   icon: 'history'  as const, label: 'History'   },
  { href: '/favorites', icon: 'star'     as const, label: 'Favorites' },
  { href: '/stats',     icon: 'chart'    as const, label: 'AI Stats'  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden md:flex flex-col py-lg px-md h-screen fixed left-0 top-0 w-[280px] bg-surface-dim border-r border-white/10 z-50">
      <div className="flex items-center gap-sm mb-xl px-4">
        <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center">
          <Music2 className="w-5 h-5 text-primary" aria-hidden="true" />
        </div>
        <div>
          <TextGradient as="div" className="text-title-lg font-bold leading-none">
            SonicPro
          </TextGradient>
          <p className="text-label-sm text-on-surface-variant">AI Playlist Engine</p>
        </div>
      </div>

      <nav aria-label="Main navigation" className="flex-1 flex flex-col gap-2">
        {navItems.map((item) => (
          <NavItem
            key={item.href}
            href={item.href}
            icon={item.icon}
            label={item.label}
            isActive={pathname === item.href}
          />
        ))}
      </nav>
    </aside>
  )
}
