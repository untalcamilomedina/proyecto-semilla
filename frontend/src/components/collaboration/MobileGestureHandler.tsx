import React, { useRef, useEffect, useState } from 'react';

interface MobileGestureHandlerProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onTap?: () => void;
  onDoubleTap?: () => void;
  onLongPress?: () => void;
  onPinch?: (scale: number) => void;
  className?: string;
}

export const MobileGestureHandler: React.FC<MobileGestureHandlerProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onTap,
  onDoubleTap,
  onLongPress,
  onPinch,
  className = ''
}) => {
  const elementRef = useRef<HTMLDivElement>(null);
  const [touchStart, setTouchStart] = useState<{ x: number; y: number; time: number } | null>(null);
  const [touchEnd, setTouchEnd] = useState<{ x: number; y: number } | null>(null);
  const [lastTap, setLastTap] = useState<number>(0);
  const [longPressTimer, setLongPressTimer] = useState<NodeJS.Timeout | null>(null);
  const [initialDistance, setInitialDistance] = useState<number>(0);

  const minSwipeDistance = 50;
  const maxTapTime = 300;
  const longPressDelay = 500;

  const getTouchDistance = (touches: TouchList): number => {
    if (touches.length < 2) return 0;
    const touch1 = touches[0];
    const touch2 = touches[1];
    return Math.sqrt(
      Math.pow(touch2.clientX - touch1.clientX, 2) +
      Math.pow(touch2.clientY - touch1.clientY, 2)
    );
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    const now = Date.now();

    setTouchStart({
      x: touch.clientX,
      y: touch.clientY,
      time: now
    });

    // Handle double tap
    if (now - lastTap < 300) {
      onDoubleTap?.();
      setLastTap(0);
    } else {
      setLastTap(now);
    }

    // Start long press timer
    const timer = setTimeout(() => {
      onLongPress?.();
      // Add haptic feedback if available
      if ('vibrate' in navigator) {
        navigator.vibrate(50);
      }
    }, longPressDelay);
    setLongPressTimer(timer);

    // Handle pinch start
    if (e.touches.length === 2) {
      setInitialDistance(getTouchDistance(e.touches));
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    // Clear long press timer on move
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }

    const touch = e.touches[0];
    setTouchEnd({
      x: touch.clientX,
      y: touch.clientY
    });

    // Handle pinch
    if (e.touches.length === 2 && initialDistance > 0) {
      const currentDistance = getTouchDistance(e.touches);
      const scale = currentDistance / initialDistance;
      onPinch?.(scale);
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    // Clear long press timer
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }

    if (!touchStart || !touchEnd) return;

    const distanceX = touchStart.x - touchEnd.x;
    const distanceY = touchStart.y - touchEnd.y;
    const isLeftSwipe = distanceX > minSwipeDistance;
    const isRightSwipe = distanceX < -minSwipeDistance;
    const isUpSwipe = distanceY > minSwipeDistance;
    const isDownSwipe = distanceY < -minSwipeDistance;

    const touchDuration = Date.now() - touchStart.time;

    // Handle swipe gestures
    if (Math.abs(distanceX) > Math.abs(distanceY)) {
      // Horizontal swipe
      if (isLeftSwipe) {
        onSwipeLeft?.();
      } else if (isRightSwipe) {
        onSwipeRight?.();
      }
    } else {
      // Vertical swipe
      if (isUpSwipe) {
        onSwipeUp?.();
      } else if (isDownSwipe) {
        onSwipeDown?.();
      }
    }

    // Handle tap (if no significant movement and short duration)
    if (Math.abs(distanceX) < 10 && Math.abs(distanceY) < 10 && touchDuration < maxTapTime) {
      onTap?.();
    }

    // Reset touch states
    setTouchStart(null);
    setTouchEnd(null);
    setInitialDistance(0);
  };

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (longPressTimer) {
        clearTimeout(longPressTimer);
      }
    };
  }, [longPressTimer]);

  return (
    <div
      ref={elementRef}
      className={className}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{
        touchAction: 'none', // Prevent default touch behaviors
        userSelect: 'none' // Prevent text selection
      }}
    >
      {children}
    </div>
  );
};