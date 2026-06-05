import { useEffect, useRef } from 'react';

interface Star {
  x: number;
  y: number;
  r: number;
  twinkle: number;
  speed: number;
  opacity: number;
}

export default function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let stars: Star[] = [];
    let animId: number;
    let w = 0, h = 0;

    function resize() {
      w = canvas!.width = window.innerWidth;
      h = canvas!.height = window.innerHeight;
    }

    function initStars() {
      const count = Math.floor((w * h) / 1800);
      stars = [];
      for (let i = 0; i < count; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: Math.random() * 1.6 + 0.3,
          twinkle: Math.random() * Math.PI * 2,
          speed: Math.random() * 0.02 + 0.005,
          opacity: Math.random() * 0.7 + 0.3,
        });
      }
    }

    function draw() {
      ctx!.clearRect(0, 0, w, h);
      for (const s of stars) {
        s.twinkle += s.speed;
        const alpha = s.opacity * (0.5 + 0.5 * Math.sin(s.twinkle));
        ctx!.beginPath();
        ctx!.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx!.fillStyle = `rgba(180,200,240,${alpha})`;
        ctx!.fill();
        if (s.r > 1.2 && alpha > 0.6) {
          ctx!.beginPath();
          ctx!.arc(s.x, s.y, s.r * 2.5, 0, Math.PI * 2);
          ctx!.fillStyle = `rgba(150,180,220,${alpha * 0.08})`;
          ctx!.fill();
        }
      }
      animId = requestAnimationFrame(draw);
    }

    resize();
    initStars();
    draw();

    const handleResize = () => { resize(); initStars(); };
    window.addEventListener('resize', handleResize);
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none"
      aria-hidden="true"
    />
  );
}
