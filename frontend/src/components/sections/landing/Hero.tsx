// Gsap
import gsap from "gsap"
import { useRef, useLayoutEffect } from "react"
import { SplitText } from "gsap/SplitText"
gsap.registerPlugin(SplitText)

// Spline 3D Wallpaper
import Spline from "../../ui/SplineWallpaper"

type HeroProps = {
  startAnimations?: boolean
}

function Hero({ startAnimations = true }: HeroProps) {
  const heroRef = useRef<HTMLDivElement | null>(null)

  useLayoutEffect(() => {
    if (!heroRef.current) return

    const ctx = gsap.context(() => {
      const memberNames = gsap.utils.toArray<HTMLElement>(".member-name")
      const memberSplits = memberNames.map((node) => new SplitText(node, { type: "chars" }))
      const memberChars = memberSplits.flatMap((split) => split.chars)

      const headingNode = heroRef.current?.querySelector<HTMLElement>(".hero-heading")
      const headingSplit = headingNode ? new SplitText(headingNode, { type: "chars" }) : null
      const headingChars = headingSplit?.chars ?? []

      const yearNode = heroRef.current?.querySelector<HTMLElement>(".hero-year")

      if (!startAnimations) {
        gsap.set(memberChars, { x: 120, opacity: 0 })
        gsap.set(headingChars, { y: 48, opacity: 0 })
        if (yearNode) gsap.set(yearNode, { y: 18, opacity: 0 })
        return
      }

      gsap.from(memberChars, {
        x: 120,
        opacity: 0,
        duration: 1,
        ease: "power4.out",
        stagger: 0.03,
        delay: 0.15,
      })

      if (headingChars.length > 0) {
        gsap.from(headingChars, {
          y: 48,
          opacity: 0,
          duration: 1,
          ease: "power4.out",
          stagger: 0.02,
          delay: 1,
        })
      }

      if (yearNode) {
        gsap.from(yearNode, {
          y: 18,
          opacity: 0,
          duration: 1,
          delay: 1.5,
          ease: "power3.out",
        })
      }

      return () => {
        memberSplits.forEach((split) => split.revert())
        headingSplit?.revert()
      }
    }, heroRef)

    return () => ctx.revert()
  }, [startAnimations])

  return (
    <div ref={heroRef} className="text-white font-tittle tracking-widest h-screen flex flex-col items-center justify-center gap-6 relative overflow-hidden">
      {/*Background 3D*/}
      <Spline startAnimations={startAnimations} />
      <div className="absolute inset-0 z-1 bg-black/75" />

      {/*Smooth Transition Background*/}
      <div className="absolute inset-x-0 top-0 h-56 z-2 bg-linear-to-t from-transparent via-black/70 to-black pointer-events-none" />
      <div className="absolute inset-x-0 bottom-0 h-56 z-2 bg-linear-to-b from-transparent via-black/70 to-black pointer-events-none" />

      {/*Main Content*/}
      <div className="relative z-10 w-full h-full flex flex-col items-center justify-center p-8 gap-6">
        {/* Team Member Names */}
        <div className="flex flex-row justify-around w-full text-xl">
          <div className="flex flex-row gap-8">
            <h2 className="member-name">Budhi Surya D.</h2>
            <h2 className="member-name">Raymond Nathaniel</h2>
          </div>
          <div className="flex flex-row gap-8 justify-end">
            <h2 className="member-name">Alika Keysia</h2>
            <h2 className="member-name">Cing Yuan</h2>
          </div>
        </div>

        {/* Main Heading */}
        <div className="text-center">
          <h1 className="hero-heading text-7xl">Break Free from Your Spotify Echo Chamber</h1>
          <h3 className="hero-year text-xl">2026</h3>
        </div>
      </div>
    </div>
  )
}

export default Hero
