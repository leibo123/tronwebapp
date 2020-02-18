const containers = document.getElementsByClassName("game");
let games = [];
let gamesCurrIndex = [];
let frameCounts = [];

function restart(index) {
  let frames = games[index];
  for (frame of frames) frame.style.display = "none";
  frames[0].style.display = "block";
  games[index] = frames;
  gamesCurrIndex[index] = 0;
}

for (container of containers) {
    let frames = container.childNodes;
    for (frame of frames) frame.style.display = "none";
    frames[0].style.display = "block";
    games.push(frames);
    gamesCurrIndex.push(0);
    frameCounts.push(frames.length);
}

document.getElementById("loading").style.display = "none";

function changeFrame() {
    for (let i = 0; i < games.length; i++) {
        let frames = games[i];
        let frameCount = frameCounts[i];
        let currIndex = gamesCurrIndex[i];

        let currFrame = Math.min(currIndex, frameCount - 1);
        frames[currFrame].style.display = "none";
        // currIndex = currIndex + 1;
        currIndex = currIndex + 1 > frameCount + 6 ? 0 : currIndex + 1;
        currFrame = Math.min(currIndex, frameCount - 1);
        frames[currFrame].style.display = "block";


        games[i] = frames;
        gamesCurrIndex[i] = currIndex;
    }
}

function searchNames() {
  // Declare variables
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById('myInput');
  filter = input.value.toUpperCase();
  ul = document.getElementById("myUL");
  li = ul.getElementsByTagName('li');

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
}

setInterval(changeFrame, 200);