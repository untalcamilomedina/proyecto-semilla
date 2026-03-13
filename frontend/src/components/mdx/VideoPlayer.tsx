/**
 * Video player component for MDX content.
 * Supports both local and external video sources.
 *
 * Usage in MDX:
 * <VideoPlayer src="/videos/intro.mp4" />
 * <VideoPlayer src="https://youtube.com/embed/..." type="youtube" />
 */
'use client';

interface VideoPlayerProps {
  src: string;
  type?: 'native' | 'youtube';
  title?: string;
  poster?: string;
}

export function VideoPlayer({
  src,
  type = 'native',
  title = 'Video',
  poster,
}: VideoPlayerProps) {
  if (type === 'youtube' || src.includes('youtube.com') || src.includes('youtu.be')) {
    const embedUrl = src.includes('/embed/')
      ? src
      : `https://www.youtube.com/embed/${extractYouTubeId(src)}`;

    return (
      <div className="my-6 glass-card p-0 overflow-hidden rounded-xl">
        <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
          <iframe
            src={embedUrl}
            title={title}
            className="absolute inset-0 w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            loading="lazy"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="my-6 glass-card p-0 overflow-hidden rounded-xl">
      <video
        src={src}
        controls
        preload="metadata"
        poster={poster}
        className="w-full rounded-xl"
        aria-label={title}
      >
        <track kind="captions" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
}

function extractYouTubeId(url: string): string {
  const match = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
  );
  return match?.[1] || '';
}
