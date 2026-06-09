import Link from 'next/link'
import { clsx } from 'clsx'
import { Sparkles, History, Star, BarChart2 } from 'lucide-react'

const tabs = [
  { href: '/',          icon: Sparkles,  label: 'Generator' },
  { href: '/history',   icon: History,   label: 'History'   },
  { href: '/favorites', icon: Star,      label: 'Favorites' },
  { href: '/stats',     icon: BarChart2, label: 'Stats'     },
]

interface BottomTabBarProps {
  currentPath: string
}

export function BottomTabBar({ currentPath }: BottomTabBarProps) {
  return (
    <nav
      aria-label="Mobile navigation"
      className="md:hidden fixed bottom-0 left-0 right-0 z-50 glass-panel border-t border-white/10 flex"
    >
      {tabs.map(({ href, icon: Icon, label }) => {
        const isActive = currentPath === href
        return (
          <Link
            key={href}
            href={href}
            aria-current={isActive ? 'page' : undefined}
            className={clsx(
              'flex-1 flex flex-col items-center gap-1 py-3 text-label-sm transition-colors focus-ring',
              isActive ? 'text-primary' : 'text-on-surface-variant',
            )}
          >
            <Icon className="w-5 h-5" aria-hidden="true" />
            <span>{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
