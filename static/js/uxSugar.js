import { CONSTANTS, state } from './base.js';

export function scrollToCurrentTopEpisode() {
  const rect = state.currentTopEpisode.getBoundingClientRect();
  const offset = CONSTANTS.SCROLL_EPISODE_OFFSET;
  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  window.scrollTo({
    top: scrollTop + rect.top - offset,
    behavior: 'smooth'
  });
}
