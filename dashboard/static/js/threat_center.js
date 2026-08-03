const feed=document.getElementById("threatFeed");

const log=document.getElementById("aiDecisionLog");

const threats=[

{

event:"Person Detected",

level:"low"

},

{

event:"Loitering",

level:"medium"

},

{

event:"Fall Detected",

level:"high"

},

{

event:"Weapon Detected",

level:"high"

}

];

function randomThreat(){

const t=threats[Math.floor(Math.random()*threats.length)];

feed.innerHTML=`

<div class="feed-item ${t.level}">

<h3>${t.event}</h3>

<p>${new Date().toLocaleTimeString()}</p>

</div>

`+feed.innerHTML;

log.innerHTML=`

<div class="ai-log">

AI Confidence :

${(90+Math.random()*10).toFixed(2)}%

</div>

`+log.innerHTML;

if(feed.children.length>8)

feed.removeChild(feed.lastChild);

if(log.children.length>8)

log.removeChild(log.lastChild);

}

setInterval(randomThreat,4000);