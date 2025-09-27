// Global animation configuration
export const animationConfig = {
  // Animation speed multiplier (1 = normal, 0.5 = half speed, 2 = double speed)
  speed: 1.0,
  
  // Individual timing controls (in seconds)
  durations: {
    entrance: 0.8,
    exit: 0.5,
    map: 0.6,
    slide: 0.3,
    listItem: 0.2,
    listItemExit: 0.1,
    stagger: 0.05,
    delay: 0.0
  },
  
  // Easing functions
  ease: {
    bounce: 'back.out(1.7)',
    mapBounce: 'back.out(1.2)',
    smooth: 'power2.out',
    exitSmooth: 'power2.in'
  }
}

// Helper function to get speed-adjusted duration
export const getDuration = (baseDuration) => baseDuration / animationConfig.speed

// Helper function to get speed-adjusted delay
export const getDelay = (baseDelay) => baseDelay / animationConfig.speed

// Helper function to log timeline duration
export const logTimelineDuration = (timeline, componentName, animationType = 'entrance') => {
  const duration = timeline.totalDuration()
  console.log(`🎬 ${componentName} ${animationType} animation duration: ${duration.toFixed(2)}s`)
  return timeline
}
