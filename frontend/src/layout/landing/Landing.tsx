import LandingNavbar from "../../components/shared/landing_navbar/LandingNavbar"
import Hero from "../../components/sections/landing/Hero"
import TheProblem from "@/components/sections/landing/TheProblem"

type LandingProps = {
  startAnimations?: boolean
}

function Landing({ startAnimations = true }: LandingProps) {
  return (
    <div>
      <LandingNavbar startAnimations={startAnimations} />

      <div className="relative z-10">
        <Hero startAnimations={startAnimations} />
        <TheProblem />
      </div>
    </div>
  )
}

export default Landing