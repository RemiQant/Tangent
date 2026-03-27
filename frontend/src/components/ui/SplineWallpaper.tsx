import { useEffect, useLayoutEffect, useRef } from 'react';
import gsap from 'gsap';
import Spline from '@splinetool/react-spline';

type SplineWallpaperProps = {
  startAnimations?: boolean
}

export default function SplineWallpaper({ startAnimations = true }: SplineWallpaperProps) {
  const splineLayerRef = useRef<HTMLDivElement | null>(null);
  const parallaxLayerRef = useRef<HTMLDivElement | null>(null);

  useLayoutEffect(() => {
    if (!splineLayerRef.current) return;

    const ctx = gsap.context(() => {
      if (!startAnimations) {
        gsap.set(splineLayerRef.current, {
          y: 36,
          opacity: 0,
          scale: 1.015,
        });
        return;
      }

      gsap.fromTo(
        splineLayerRef.current,
        {
          y: 48,
          opacity: 0,
          scale: 1.015,
        },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 1.2,
          ease: 'power3.out',
          delay: 0.14,
        }
      );
    }, splineLayerRef);

    return () => ctx.revert();
  }, [startAnimations]);

  useEffect(() => {
    if (!parallaxLayerRef.current) return;

    const yTo = gsap.quickTo(parallaxLayerRef.current, 'y', {
      duration: 0.65,
      ease: 'power3.out',
    });

    const handleScroll = () => {
      yTo(window.scrollY * -0.18);
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <div ref={splineLayerRef} className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
      <div
        ref={parallaxLayerRef}
        className="w-full h-full will-change-transform"
      >
        <Spline
          scene="https://prod.spline.design/EfP3R-yLTHrjUOta/scene.splinecode"
          className="w-full h-full"
        />
      </div>
    </div>
  );
}