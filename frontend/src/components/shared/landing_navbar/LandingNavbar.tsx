// Button component
import { Button } from "@/components/ui/Button"
import { useNavigate } from "react-router-dom"

//Gsap animation classes
import gsap from "gsap"
import { useLayoutEffect, useRef } from "react"

// Icons
import { CiMusicNote1 } from "react-icons/ci"

type LandingNavbarProps = {
  startAnimations?: boolean
}

function LandingNavbar({ startAnimations = true }: LandingNavbarProps) {
  // Hover animation classes
  const hover = 'relative group hover:text-orange-500 duration-300 transition-colors'
  const line = 'absolute bottom-0 left-0 w-0 h-1 bg-orange-500 group-hover:w-full duration-300 transition-all -mb-2'

  // Navigation
  const navigate = useNavigate()

  // GSAP animation for navbar entrance
  const navRef = useRef<HTMLElement | null>(null)
  useLayoutEffect(() => {
    if (!navRef.current) return

    const ctx = gsap.context(() => {
      if (!startAnimations) {
        gsap.set(navRef.current, { y: -24, opacity: 0 })
        return
      }

      gsap.fromTo(
        navRef.current,
        { y: -32, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, delay: 0.7, ease: "power3.out" }
      )
    }, navRef)

    return () => ctx.revert()
  }, [startAnimations])

  return (
    <nav ref={navRef} className="p-8 text-white flex flex-row justify-between tracking-widest fixed top-0 left-0 right-0 z-50">
      {/*Website Name*/}
      <div className="flex flex-row gap-4">
        <CiMusicNote1 className="text-4xl text-orange-500" />
        <h1 className="font-tittle text-4xl">Tangent.</h1>
      </div>

      {/*Nav Menu List*/}
      <div className="flex items-center justify-center">
        <ul className="flex flex-row gap-7 font-tittle text-gray-400">
          <li><a href="" className={hover}><span className={line}></span>Home</a></li>
          <li><a href="" className={hover}><span className={line}></span>The Problem</a></li>
          <li><a href="" className={hover}><span className={line}></span>How It Works</a></li>
          <li><a href="" className={hover}><span className={line}></span>The Output Showcase</a></li>
          <li><a href="" className={hover}><span className={line}></span>Final CTA & Footer</a></li>
        </ul>
      </div>

      {/*Auth*/}
      <div className="flex gap-6">
        <Button onClick={() => navigate('/login')} variant="outline" size="lg">Log In</Button>
        <Button onClick={() => navigate('/signup')} variant="outline" size="lg">Sign Up</Button>
      </div>
    </nav>
  )
}

export default LandingNavbar