export const CONSTANTS = {
  MAX_EPISODE_TITLE_WIDTH: 375,
  EPISODE_TITLE_MARQUEE_SPEED: 95,
  MARQUEE_FOCUS_TIME_DELAY: 1,
  SCROLL_DEBOUNCE_TIME: 500,
  PLAYBACK_LOG_INTERVAL: 3000,
  MARQUEE_CHECK_INTERVAL: 100,
  SCROLL_OFFSET: 75,
  SKIP_TIME: 15, 
  SCROLL_EPISODE_OFFSET: 60,

  API_URLS: {
    SET_PLAYBACK_TIME: '/set-episode-playback-time',
    HIDE_EPISODE: '/hide-episode',
    DOWNLOAD_EPISODE: '/download-episode',
    PLAY_EPISODE: '/play-episode',
    TOGGLE_CHRONOLOGICAL: '/toggle-feed-chronological',
    HIDE_ALL_EPISODES: '/hide-all-episodes',
    REFRESH_SUBSCRIPTIONS: '/refresh-subscriptions',
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
  lastRecordedPlaybackTime: 0
};

import { debounce } from './utils.js';
import { findTopEpisodeElement } from './uiMeasure.js';
import ApiService from './apiService.js';
import AudioPlayer from './audioPlayer.js';
import EpisodeManager from './episodeManager.js';
import { scrollToCurrentTopEpisode } from './uxSugar.js';
import { addMarqueeEffect, removeMarqueeEffect } from './marquee.js';

const episodeManager = new EpisodeManager();
window.hideEpisode = episodeManager.hideEpisode.bind(episodeManager);
window.downloadEpisode = episodeManager.downloadEpisode.bind(episodeManager);
window.playEpisode = episodeManager.playEpisode.bind(episodeManager);
window.hideAll = episodeManager.hideAll.bind(episodeManager);
window.refreshFeed = episodeManager.refreshFeed.bind(episodeManager);
window.toggleChron = episodeManager.toggleChron.bind(episodeManager);
const audioPlayer = new AudioPlayer();
window.setPlayerToTime = audioPlayer.setTime.bind(audioPlayer);

const logPlaybackTime = async () => {
  const currentTime = audioPlayer.getCurrentTime();
  if (typeof currentTime !== 'number' || currentTime === 0 || currentTime === state.lastRecordedPlaybackTime) {
    return;
  }
  try {
    state.lastRecordedPlaybackTime = currentTime;
    await ApiService.post(CONSTANTS.API_URLS.SET_PLAYBACK_TIME, currentTime);
  } catch (error) {
    alert(error)
  }
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
setInterval(logPlaybackTime, CONSTANTS.PLAYBACK_LOG_INTERVAL);

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
