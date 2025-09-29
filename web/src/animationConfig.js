

/**
 * Global animation configuration object for controlling animation speeds, durations, and easings.
 * @type {Object}
 * @property {number} speed - Animation speed multiplier (1 = normal, 0.5 = half speed, 2 = double speed)
 * @property {Object} durations - Individual timing controls (in seconds)
 * @property {Object} ease - Easing functions for different animation types
 */
export const animationConfig = {
  speed: 1.0,
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
  ease: {
    bounce: 'back.out(1.7)',
    mapBounce: 'back.out(1.2)',
    smooth: 'power2.out',
    exitSmooth: 'power2.in'
  }
}


/**
 * Returns the speed-adjusted duration for an animation.
 * @param {number} baseDuration - The base duration in seconds.
 * @returns {number} Speed-adjusted duration.
 */
export const getDuration = (baseDuration) => baseDuration / animationConfig.speed

/**
 * Returns the speed-adjusted delay for an animation.
 * @param {number} baseDelay - The base delay in seconds.
 * @returns {number} Speed-adjusted delay.
 */
export const getDelay = (baseDelay) => baseDelay / animationConfig.speed

/**
 * Logs the total duration of a GSAP timeline for debugging purposes.
 * @param {Object} timeline - GSAP timeline instance.
 * @param {string} componentName - Name of the component.
 * @param {string} [animationType='entrance'] - Type of animation.
 * @returns {Object} The timeline instance.
 */
export const logTimelineDuration = (timeline, componentName, animationType = 'entrance') => {
  const duration = timeline.totalDuration()
  console.log(`${componentName} ${animationType} animation duration: ${duration.toFixed(2)}s`)
  return timeline
}
