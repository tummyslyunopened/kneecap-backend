const episodeTitleSelector = '[id^="episode-title-"]';
const maxEpisodeTitleWidth = 355;
const episodeTitleMarqueeSpeed = 95;
const marqueeFocusTimeDelay = 1;

let lastTopEpisode = null;
let lastScrollTime = null;


function topElement(selector) {
  const elements = document.querySelectorAll(selector);
  let topEpisode = null;
  let topEpisodeDistance = Infinity;

  elements.forEach(element => {
    const rect = element.getBoundingClientRect();
    const distance = rect.top;
    if (distance >= 0 && distance < topEpisodeDistance) {
      topEpisodeDistance = distance;
      topEpisode = element;
    }
  });
  return topEpisode
}

function getMarqueeKeyframeParams(distance, speed, delay) {
  let animationTime = distance / speed
  let totalTime = 2 * delay + animationTime
  let beginAnimationPercentage = 100 * delay / totalTime
  let endAnimationPercentage = beginAnimationPercentage + 100 * animationTime / totalTime
  return {
    distance: distance,
    totalTime: totalTime,
    beginAnimationPercentage: beginAnimationPercentage,
    endAnimationPercentage: endAnimationPercentage
  }
}

function marqueeTitle() {
  topEpisode = topElement(episodeTitleSelector)
  if (topEpisode) {

    if (lastTopEpisode && lastTopEpisode !== topEpisode) {
      lastTopEpisode.style.color = '';
      lastTopEpisode.style.whiteSpace = '';
      lastTopEpisode.style.overflow = '';
      lastTopEpisode.style.position = '';
      lastTopEpisode.style.animation = '';
      lastTopEpisode = topEpisode;
    }
    const titleWidth = topEpisode.offsetWidth;
    if (titleWidth > maxEpisodeTitleWidth) {
      let overflowWidth = titleWidth - maxEpisodeTitleWidth
      marqueeParams = getMarqueeKeyframeParams(overflowWidth, episodeTitleMarqueeSpeed, marqueeFocusTimeDelay)

      topEpisode.style.whiteSpace = 'nowrap';
      topEpisode.style.overflow = 'hidden';
      topEpisode.style.position = 'relative';

      const keyframes = `
        @keyframes scroll-left {
          0% {
            transform: translateX(0); /* Start from the initial position */
          }
          ${marqueeParams.beginAnimationPercentage}% {
            transform: translateX(0); /* Start from the initial position */
          }
          ${marqueeParams.endAnimationPercentage}% {
            transform: translateX(-${marqueeParams.distance}px); /* Scroll to the left based on text width */
          }
          100% {
            transform: translateX(-${marqueeParams.distance}px); /* Scroll to the left based on text width */
          }
        }
      `;

      const styleSheet = document.createElement("style");
      styleSheet.type = "text/css";
      styleSheet.innerText = keyframes;
      document.head.appendChild(styleSheet);
      topEpisode.style.animation = 'scroll-left ' + (marqueeParams.totalTime) + 's linear infinite';
      lastTopEpisode = topEpisode;
    }
  }
}


function episodeMethodPost(url, episodeId) {
  $.ajax({
    type: "POST",
    url: url,
    data: {
      'episode_id': episodeId,
      'csrfmiddlewaretoken': window.CSRF_TOKEN
    }
  });
}

function simplePost(url, data=null) {
  $.ajax({
    type: "POST",
    url: url,
    data: {
      'data': data,
      'csrfmiddlewaretoken': window.CSRF_TOKEN
    }
  });
}

function hideEpisode(url, episodeId) {
  episodeMethodPost(url, episodeId)
  let el = document.getElementById(episodeId);
  el.remove()
  lastTopEpisode = null;
}

function downloadEpisode(url, episodeId) {
  episodeMethodPost(url, episodeId);
  let el = document.getElementById('episode-download-btn-' + episodeId);
  el.disabled = true;
  el.innerHTML = "Queued"
}

function playEpisode(url, episodeId) {
  episodeMethodPost(url, episodeId);
}

function toggleChron(url) {
  simplePost(url);
  el = document.getElementById('episode-previews');
  const children = Array.from(el.children);
  children.reverse();
  el.innerHTML = ''; 
  children.forEach(child => el.appendChild(child)); // Reappend children in reversed order
  window.scrollTo(0, 0); 
  lastScrollTime = new Date().getTime() + 5000;
}

function logCurrentPlaybackTime() {
  const currentTime = document.getElementById('player-audio').currentTime;
  console.log(currentTime)
  simplePost('/set-episode-playback-time', currentTime)
}

function setPlayerToTime(time) {
  document.getElementById('player-audio').currentTime = time;
}

document.addEventListener('keydown', function (event) {
  if (event.code === 'Space') {
    event.preventDefault(); // Prevent scrolling the page
    var audio = document.getElementById('player-audio');
    if (audio.paused) {
      audio.play();
    } else {
      audio.pause();
    }
  }
});

setInterval(logCurrentPlaybackTime, 3000);
setInterval(marqueeTitle, 100);
setTimeout(initEpisodePreviewGestures, 2000);
setInterval(() => {
  const currentTime = new Date().getTime();
  if (currentTime - lastScrollTime > 500 && lastTopEpisode) {
    window.scrollTo({ top: lastTopEpisode.offsetTop - 75, behavior: 'smooth' });
  }
}, 100);

window.addEventListener('scroll', function () {
  lastScrollTime = new Date().getTime();
});

function initEpisodePreviewGestures() {
  el = document.getElementById('episode-previews');
  const children = Array.from(el.children);
  children.forEach(child => {

    child.addEventListener('touchstart', function (event) {
      console.log(event)
      touchstartX = event.changedTouches[0].screenX;
      touchstartY = event.changedTouches[0].screenY;
    }, false);

    child.addEventListener('touchend', function (event) {
      touchendX = event.changedTouches[0].screenX;
      touchendY = event.changedTouches[0].screenY;
      handleGesture();
    }, false);
    
    function handleGesture() {
      if (touchendX < touchstartX) {
        console.log('Swiped Left');
      }

      if (touchendX > touchstartX) {
        console.log('Swiped Right');
      }

      if (touchendY < touchstartY) {
        console.log('Swiped Up');
      }

      if (touchendY > touchstartY) {
        console.log('Swiped Down');
      }

      if (touchendY === touchstartY) {
        console.log('Tap');
      }
    }
  });
}
