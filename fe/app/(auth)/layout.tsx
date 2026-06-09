export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh bg-background flex items-center justify-center">
      {children}
    </div>
  )
}
