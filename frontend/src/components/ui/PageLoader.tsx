type PageLoaderProps = {
  isVisible: boolean
}

function PageLoader({ isVisible }: PageLoaderProps) {
  return (
    <div
      className={`fixed inset-0 z-9999 flex items-center justify-center bg-black transition-opacity duration-700 ${
        isVisible ? "opacity-100" : "pointer-events-none opacity-0"
      }`}
      aria-hidden={!isVisible}
    >
      <div className="flex flex-col items-center gap-5">
        <h1 className="font-tittle text-5xl tracking-widest text-white">Tangent.</h1>
        <div className="flex items-end gap-2" role="status" aria-label="Loading">
          {[0, 1, 2, 3, 4].map((item) => (
            <span
              key={item}
              className="inline-block w-2 rounded-sm bg-orange-500"
              style={{
                height: `${14 + item * 6}px`,
                animation: "loaderBeat 0.8s ease-in-out infinite",
                animationDelay: `${item * 0.08}s`,
              }}
            />
          ))}
        </div>
      </div>

      <style>{`
        @keyframes loaderBeat {
          0%, 100% { transform: scaleY(0.55); opacity: 0.6; }
          50% { transform: scaleY(1); opacity: 1; }
        }
      `}</style>
    </div>
  )
}

export default PageLoader
