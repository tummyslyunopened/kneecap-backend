const episodeTitleSelector = '[id^="episode-title-"]';
const maxEpisodeTitleWidth = 375; 
const episodeTitleMarqueeSpeed = 95; 
const marqueeFocusTimeDelay = 1; 

let lastTopEpisode = null; 


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
  console.log(topEpisode)
  return topEpisode
}

function getMarqueeKeyframeParams(distance, speed, delay){
 let animationTime = distance / speed
 let totalTime = 2*delay + animationTime
 let beginAnimationPercentage = 100 * delay / totalTime
 let endAnimationPercentage = beginAnimationPercentage + 100 * animationTime / totalTime 
 return {
  distance:distance,
  totalTime:totalTime,
  beginAnimationPercentage:beginAnimationPercentage,
  endAnimationPercentage:endAnimationPercentage
 }
}

function marqueeTitle(){
 console.log("attempting title marquee") 
 console.log(episodeTitleSelector)  
 topEpisode = topElement(episodeTitleSelector)
  if (topEpisode) {
    
    if (lastTopEpisode && lastTopEpisode !== topEpisode) {
      lastTopEpisode.style.color = ''; 
      lastTopEpisode.style.whiteSpace = ''; 
      lastTopEpisode.style.overflow = ''; 
      lastTopEpisode.style.position = ''; 
      lastTopEpisode.style.animation = ''; 
    }
    const titleWidth = topEpisode.offsetWidth;
    if (titleWidth > maxEpisodeTitleWidth) {
      let overflowWidth = titleWidth - maxEpisodeTitleWidth
      marqueeParams = getMarqueeKeyframeParams(overflowWidth, episodeTitleMarqueeSpeed, marqueeFocusTimeDelay)

      topEpisode.style.color = 'red'; 
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

function simplePost(url){
        $.ajax({
            type: "POST",
            url: url,
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN
            }
        });
}

function hideEpisode(url, episodeId) {
  episodeMethodPost(url, episodeId)
  let el = document.getElementById(episodeId);
  el.style.display = "none";
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
  el.innerHTML = ''; // Clear the container
  children.forEach(child => el.appendChild(child)); // Reappend children in reversed order
}
function logCurrentPlaytime() {
  const audioElement = document.getElementById('player-audio');
  console.log(audioElement.currentTime);
}

setInterval(logCurrentPlaytime, 3000);


window.addEventListener('scroll', marqueeTitle);
