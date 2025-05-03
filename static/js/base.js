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

  API_URLS: {
    SET_PLAYBACK_TIME: '/set-episode-playback-time',
    HIDE_EPISODE: '/hide-episode',
    DELETE_SUBSCRIPTION: '/delete-subscription',
    DOWNLOAD_EPISODE: '/download-episode',
    PLAY_EPISODE: '/play-episode',
    TOGGLE_CHRONOLOGICAL: '/toggle-feed-chronological',
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
  lastRecordedPlaybackTime: 0,
  lastSentPlaybackTime: 0,
  transcript_visible: false
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

// Bind submodule methods to window
const episodeManager = new EpisodeManager();
window.hideEpisode = episodeManager.hideEpisode.bind(episodeManager);
window.downloadEpisode = episodeManager.downloadEpisode.bind(episodeManager);
window.playEpisode = episodeManager.playEpisode.bind(episodeManager);
window.hideAll = episodeManager.hideAll.bind(episodeManager);
window.toggleChron = episodeManager.toggleChron.bind(episodeManager);

const audioPlayer = new AudioPlayer();
window.setPlayerToTime = audioPlayer.setTime.bind(audioPlayer);
window.audioPlayer = audioPlayer;

const subscriptionManager = new SubscriptionManager();
window.deleteSubscription = subscriptionManager.deleteSubscription.bind(subscriptionManager);

// Initialize TranscriptManager
const transcriptManager = new TranscriptManager();

// Bind TranscriptManager methods to window
window.showTranscript = transcriptManager.showTranscript.bind(transcriptManager);
window.hideTranscript = transcriptManager.hideTranscript.bind(transcriptManager);
window.startTranscriptUpdateInterval = transcriptManager.startUpdateInterval.bind(transcriptManager);
window.stopTranscriptUpdateInterval = transcriptManager.stopUpdateInterval.bind(transcriptManager);

// Bind transcript methods
window.showTranscript = () => {
    transcriptManager.showTranscript();
    transcriptManager.startUpdateInterval();
};

window.hideTranscript = () => {
    transcriptManager.hideTranscript();
    transcriptManager.stopUpdateInterval();
};

window.styleActiveTranscriptSegment = transcriptManager.styleActiveTranscriptSegment;

// other global functions

const logPlaybackTime = async () => {
  if (!window.audioPlayer || !window.audioPlayer.audio) {
    console.log('Audio Player not Found')
    return; // Don't do anything if audio player isn't ready
  }
  const currentTime = window.audioPlayer.getCurrentTime();
  // console.log('logPlaybackTime called - current time:', currentTime);
  if (typeof currentTime !== 'number' || isNaN(currentTime)) {
    console.log('Invalid time:', currentTime);
    return; // Don't update if we don't have a valid time
  }
  state.lastRecordedPlaybackTime = currentTime;
  if (Math.abs(currentTime - state.lastSentPlaybackTime) >= CONSTANTS.PLAYBACK_LOG_INTERVAL) {
    state.lastSentPlaybackTime = currentTime;
    console.log('Sending time to API:', currentTime);
    await ApiService.post(CONSTANTS.API_URLS.SET_PLAYBACK_TIME, currentTime);
  }
  // console.log('Current time:', currentTime, 'Last sent time:', state.lastSentPlaybackTime);
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

// Intervals
setInterval(logPlaybackTime, 1 );

// Event Listeners
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
