import { CONSTANTS, state } from './base.js';

function getMarqueeKeyframeParams(distance, speed, delay) {
  const animationTime = distance / speed;
  const totalTime = 2 * delay + animationTime;
  const beginAnimationPercentage = 100 * delay / totalTime;
  const endAnimationPercentage = beginAnimationPercentage + 100 * animationTime / totalTime;
  return {
    distance,
    totalTime,
    beginAnimationPercentage,
    endAnimationPercentage,
  };
}

export function addMarqueeEffect(element, maxWidth) {
  if (!element) return;
  removeMarqueeEffect(element);
  const titleWidth = element.offsetWidth;
  if (titleWidth <= maxWidth) {
    return;
  }
  const speed = CONSTANTS.EPISODE_TITLE_MARQUEE_SPEED;
  const delay = CONSTANTS.MARQUEE_FOCUS_TIME_DELAY;
  const params = getMarqueeKeyframeParams(titleWidth - maxWidth, speed, delay);
  const keyframes = `
    @keyframes scroll-left {
      0%, ${params.beginAnimationPercentage}% {
        transform: translateX(0);
      }
      ${params.endAnimationPercentage}%, 100% {
        transform: translateX(-${params.distance}px);
      }
    }
  `;
  if (state.marqueeStyleSheet) {
    document.head.removeChild(state.marqueeStyleSheet);
  }
  state.marqueeStyleSheet = document.createElement("style");
  state.marqueeStyleSheet.type = "text/css";
  state.marqueeStyleSheet.innerText = keyframes;
  document.head.appendChild(state.marqueeStyleSheet);
  element.style.animation = `scroll-left ${params.totalTime}s linear infinite`;
}

export function removeMarqueeEffect(element) {
  if (element) {
    element.style.animation = '';
    element.style.transform = '';
  }
  if (state.marqueeStyleSheet) {
    document.head.removeChild(state.marqueeStyleSheet);
    state.marqueeStyleSheet = null;
  }
}
