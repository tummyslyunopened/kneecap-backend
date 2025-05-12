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
  marqueeStyleSheet: null,
  ...(document.getElementById('initial-playback-time') ? {
    lastRecordedPlaybackTime: parseFloat(document.getElementById('initial-playback-time').textContent) || 0,
    lastSentPlaybackTime: parseFloat(document.getElementById('initial-playback-time').textContent) || 0
  } : {}),
  transcript_visible: false,
  isAutoplayEnabled: document.getElementById('autoplay-toggle')?.checked || false,
  lastAutoplayTime: 0,
};

import { debounce } from './utils.js';
import { findTopEpisodeElement } from './uiMeasure.js';
import ApiService from './apiService.js';
import AudioPlayer from './audioPlayer.js';
import EpisodeManager from './episodeManager.js';
import SubscriptionManager from './subscriptionManager.js';
import { scrollToCurrentTopEpisode } from './uxSugar.js';
import { addMarqueeEffect, removeMarqueeEffect } from './marquee.js';
import { TranscriptManager } from './transcriptManager.js';

const subscriptionManager = new SubscriptionManager();
window.deleteSubscription = subscriptionManager.deleteSubscription.bind(subscriptionManager)

const episodeManager = new EpisodeManager();
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
const checkAutoplay = async () => {
  if (!state.isAutoplayEnabled || !audioPlayer) {
    return;
  }
  const timeSinceLastAutoplay = Date.now() - state.lastAutoplayTime;
  if (timeSinceLastAutoplay < CONSTANTS.AUTOCOOLDOWN) {
    return;
  }
  const currentTime = audioPlayer.getCurrentTime();
  const duration = audioPlayer.audio.duration;
  if (duration - currentTime <= CONSTANTS.AUTOPLAY_THRESHOLD) {
    const nextEpisodeId = getNextEpisode();
    if (nextEpisodeId) {
      const currentEpisodeId = document.getElementById('player-id').textContent.trim();
      await window.hideEpisode(currentEpisodeId);
      await window.playEpisode(nextEpisodeId);
      state.lastAutoplayTime = Date.now();
    }
  }
};

const logPlaybackTime = async () => {
  if (!audioPlayer) {
    console.warn('Audio player not found when attempting to log playback time')
    return;
  }
  const currentTime = audioPlayer.getCurrentTime();
  if (typeof currentTime !== 'number' || isNaN(currentTime)) {
    console.warn('Invalid time detected for audioPlayer:', currentTime);
    return;
  }
  state.lastRecordedPlaybackTime = currentTime;
  if (Math.abs(currentTime - state.lastSentPlaybackTime) >= CONSTANTS.PLAYBACK_LOG_INTERVAL) {
    state.lastSentPlaybackTime = currentTime;
    console.info('Sending time to API:', currentTime);
    ApiService.post(CONSTANTS.API_URLS.SET_PLAYBACK_TIME, currentTime);
  }
  await checkAutoplay();
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
setInterval(logPlaybackTime, 1);
window.addEventListener('scroll', handleScroll);
state.currentTopEpisode = findTopEpisodeElement();
addMarqueeEffect(state.currentTopEpisode.querySelector('.episode-title'), CONSTANTS.MAX_EPISODE_TITLE_WIDTH);
document.addEventListener('DOMContentLoaded', () => {
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
});
