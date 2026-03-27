// import Dashboard from "./layout/dashboard/Dashboard"
import { useEffect, useRef, useState } from "react"
import PageLoader from "./components/ui/PageLoader"
import Landing from "./layout/landing/Landing"


function App() {
  const [isLoading, setIsLoading] = useState(true)
  const [showLoader, setShowLoader] = useState(true)
  const mountedAtRef = useRef<number>(Date.now())

  useEffect(() => {
    const previousScrollRestoration = window.history.scrollRestoration
    window.history.scrollRestoration = "manual"
    window.scrollTo({ top: 0, left: 0, behavior: "auto" })

    const finishLoading = () => {
      const elapsed = Date.now() - mountedAtRef.current
      const minDuration = 900
      const waitTime = Math.max(0, minDuration - elapsed)

      window.setTimeout(() => {
        // Keep the initial viewport anchored to the hero section.
        window.scrollTo({ top: 0, left: 0, behavior: "auto" })
        setIsLoading(false)
        window.setTimeout(() => setShowLoader(false), 700)
      }, waitTime)
    }

    if (document.readyState === "complete") {
      finishLoading()
      return
    }

    window.addEventListener("load", finishLoading, { once: true })

    // Fallback so loader never gets stuck if some resource fails.
    const fallbackId = window.setTimeout(finishLoading, 5000)

    return () => {
      window.removeEventListener("load", finishLoading)
      window.clearTimeout(fallbackId)
      window.history.scrollRestoration = previousScrollRestoration
    }
  }, [])

  return (
    <>
      {showLoader && <PageLoader isVisible={isLoading} />}
      <Landing startAnimations={!isLoading} />
    </>
  )
}

export default App
