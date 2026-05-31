import React from 'react'

interface LinkProps {
  href: string
  children: React.ReactNode
  className?: string
  'aria-current'?: string | boolean
  [key: string]: unknown
}

function NextLink({ href, children, className, ...rest }: LinkProps) {
  return (
    <a href={href} className={className} {...rest}>
      {children}
    </a>
  )
}

export default NextLink
