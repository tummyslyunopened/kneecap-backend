export const CONSTANTS = {
  MAX_EPISODE_TITLE_WIDTH: 375,
  EPISODE_TITLE_MARQUEE_SPEED: 95,
  MARQUEE_FOCUS_TIME_DELAY: 1,
  SCROLL_DEBOUNCE_TIME: 500,
  PLAYBACK_LOG_INTERVAL: 10,
  MARQUEE_CHECK_INTERVAL: 100,
  SCROLL_OFFSET: 75,
  SKIP_TIME: 15,
  SCROLL_EPISODE_OFFSET: 60,
  AUTOPLAY_THRESHOLD: 10,
  AUTOCOOLDOWN: 5000,

  API_URLS: {
    SET_PLAYBACK_TIME: '/set-episode-playback-time',
    HIDE_EPISODE: '/hide-episode',
    DELETE_SUBSCRIPTION: '/delete-subscription',
    DOWNLOAD_EPISODE: '/download-episode',
    PLAY_EPISODE: '/play-episode',
    TOGGLE_CHRONOLOGICAL: '/toggle-feed-chronological',
    TOGGLE_AUTOPLAY: '/toggle-feed-autoplay',
    HIDE_ALL_EPISODES: '/hide-all-episodes',
  },

  KEYBOARD_SHORTCUTS: {
    PLAY_PAUSE: ' ',
    SKIP_FORWARD: 'ArrowRight',
    SKIP_BACKWARD: 'ArrowLeft',
    VOLUME_UP: 'ArrowUp',
    VOLUME_DOWN: 'ArrowDown',
  },
};

export const state = {
  lastScrollTime: Date.now(),
  lastTopEpisode: null,
  currentTopEpisode: null,
  isPlaying: false,
  lastRecordedIsPlaying: false,
  marqueeStyleSheet: null,
  ...(document.getElementById('initial-playback-time') ? {
    lastRecordedPlaybackTime: parseFloat(document.getElementById('initial-playback-time').textContent) || 0,
    lastSentPlaybackTime: parseFloat(document.getElementById('initial-playback-time').textContent) || 0
  } : {}),
  transcript_visible: false,
  isFollowScroll: true,
  isAutoplayEnabled: document.getElementById('autoplay-toggle')?.checked || false,
  lastAutoplayTime: 0,
  playbackRate: 1.0
};

import { debounce } from './utils.js';
import { findTopEpisodeElement } from './uiMeasure.js';
import AudioPlayer from './audioPlayer.js';
import EpisodeManager from './episodeManager.js';
import SubscriptionManager from './subscriptionManager.js';
import { scrollToCurrentTopEpisode } from './uxSugar.js';
import { addMarqueeEffect, removeMarqueeEffect } from './marquee.js';
import { TranscriptManager } from './transcriptManager.js';
import { isMobileDevice } from './mobile.js';

const subscriptionManager = new SubscriptionManager();
window.deleteSubscription = subscriptionManager.deleteSubscription.bind(subscriptionManager)

// Add toggleMenu to window object
window.toggleMenu = () => {
  const menuContent = document.getElementById('menu-content');
  menuContent.classList.toggle('show');
  
  // Close the menu when clicking outside
  const closeMenu = (e) => {
    if (!e.target.matches('.menu-btn')) {
      menuContent.classList.remove('show');
      document.removeEventListener('click', closeMenu);
    }
  };
  document.addEventListener('click', closeMenu);
};

const episodeManager = new EpisodeManager();
window.updateQueueDuration = () => {
  episodeManager.updateQueueDuration();
  episodeManager.startUpdateInterval();
}
window.updateQueueDuration(); 
window.hideEpisode = episodeManager.hideEpisode.bind(episodeManager);
window.downloadEpisode = episodeManager.downloadEpisode.bind(episodeManager);
window.playEpisode = episodeManager.playEpisode.bind(episodeManager);
window.hideAll = episodeManager.hideAll.bind(episodeManager);
window.toggleChron = episodeManager.toggleChron.bind(episodeManager);
window.toggleAutoplay = episodeManager.toggleAutoplay.bind(episodeManager);

const audioPlayer = new AudioPlayer();
window.setPlayerToTime = audioPlayer.setTime.bind(audioPlayer);
setPlayerToTime(state.lastRecordedPlaybackTime)

const transcriptManager = new TranscriptManager();
window.showTranscript = () => {
  transcriptManager.showTranscript();
  transcriptManager.startUpdateInterval();
};
window.hideTranscript = () => {
  transcriptManager.hideTranscript();
  transcriptManager.stopUpdateInterval();
};
window.toggleFollowScroll = transcriptManager.toggleFollowScroll.bind(transcriptManager);
const getNextEpisode = () => {
  const episodePreviews = document.querySelectorAll('.episode-preview');
  if (!episodePreviews.length) return null;
  const currentEpisodeId = document.getElementById('player-id').textContent.trim();
  for (const preview of episodePreviews) {
    if (preview.id === currentEpisodeId) continue;
    return preview.id;
  }
  return null;
};


// Check if we should autoplay the next episode
const checkAutoplay = async () => {
  if (!state.isAutoplayEnabled || !audioPlayer || !audioPlayer.audio) {
    return false;
  }
  
  const timeSinceLastAutoplay = Date.now() - state.lastAutoplayTime;
  if (timeSinceLastAutoplay < CONSTANTS.AUTOCOOLDOWN) {
    return false;
  }
  
  const currentTime = audioPlayer.getCurrentTime();
  const duration = audioPlayer.audio.duration;
  
  if (duration - currentTime <= CONSTANTS.AUTOPLAY_THRESHOLD) {
    const nextEpisodeId = getNextEpisode();
    if (nextEpisodeId) {
      const currentEpisodeId = document.getElementById('player-id')?.textContent.trim();
      if (currentEpisodeId) {
        await window.hideEpisode(currentEpisodeId);
      }
      await window.playEpisode(nextEpisodeId);
      state.lastAutoplayTime = Date.now();
      return true;
    }
  }
  return false;
};

const handleScroll = debounce(() => {
  state.lastScrollTime = Date.now();
  state.lastTopEpisode = state.currentTopEpisode;
  state.currentTopEpisode = findTopEpisodeElement();
  if (state.currentTopEpisode) {
    scrollToCurrentTopEpisode();
    const titleElem = state.currentTopEpisode.querySelector('.episode-title');
    const lastTitleElem = state.lastTopEpisode && state.lastTopEpisode.querySelector
      ? state.lastTopEpisode.querySelector('.episode-title')
      : null;
    if (state.lastTopEpisode !== state.currentTopEpisode) {
      removeMarqueeEffect(lastTitleElem, CONSTANTS.MAX_EPISODE_TITLE_WIDTH);
    } else {
      addMarqueeEffect(titleElem, CONSTANTS.MAX_EPISODE_TITLE_WIDTH);
    }
  }
}, CONSTANTS.SCROLL_DEBOUNCE_TIME);
window.addEventListener('scroll', handleScroll);
state.currentTopEpisode = findTopEpisodeElement();
addMarqueeEffect(state.currentTopEpisode.querySelector('.episode-title'), CONSTANTS.MAX_EPISODE_TITLE_WIDTH);
document.addEventListener('DOMContentLoaded', () => {
  // Initialize episode preview marquees
  const previews = document.querySelectorAll('.episode-preview');
  previews.forEach(preview => {
    const title = preview.querySelector('.episode-title');
    preview.addEventListener('mouseenter', () => {
      addMarqueeEffect(title, CONSTANTS.MAX_EPISODE_TITLE_WIDTH);
    });
    preview.addEventListener('mouseleave', () => {
      removeMarqueeEffect(title, CONSTANTS.MAX_EPISODE_TITLE_WIDTH);
    });
  });

  // Mobile-specific logic
  if (isMobileDevice()) {
    const stickyFooterElems = document.querySelectorAll('.sticky-footer');
    stickyFooterElems.forEach(elem => {
      elem.classList.add('sticky-footer-mobile');
      elem.classList.remove('sticky-footer');
    });
    const stickyHeaderElems = document.querySelectorAll('.sticky-header');
    stickyHeaderElems.forEach(elem => {
      elem.classList.add('sticky-header-mobile');
      elem.classList.remove('sticky-header');
    });
    const queueSummaryElems = document.querySelectorAll('.queue-summary');
    queueSummaryElems.forEach(elem => {
      elem.classList.add('queue-summary-mobile');
      elem.classList.remove('queue-summary');
    });
    // Disable horizontal scrolling
    document.body.style.overflowX = 'hidden';
    document.documentElement.style.overflowX = 'hidden';
  }
});
