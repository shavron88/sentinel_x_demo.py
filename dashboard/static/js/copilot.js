function sendQuestion(){

const input=document.getElementById("userQuestion");

if(input.value==="") return;

const chat=document.getElementById("chatWindow");

chat.innerHTML+=`

<div class="user-message">

${input.value}

</div>

`;

chat.innerHTML+=`

<div class="ai-message">

Thinking...

</div>

`;

chat.scrollTop=chat.scrollHeight;

input.value="";

}