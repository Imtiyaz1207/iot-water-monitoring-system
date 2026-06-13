
/* ------------------------------------ javascript functions -------------------------------------------------------------------------------------------------------*/
const socket = io();

function control(cmd){

fetch(`/device/${cmd}`);

log(cmd);

}

function setMode(mode){

fetch(`/mode/${mode}`);

document.getElementById(

"modeStatus"

).innerHTML=

mode.toUpperCase();

}

function log(text){

let a = document.getElementById(

"activity"

);

a.innerHTML += text+"<br>";

a.scrollTop=a.scrollHeight;

}

function updateStatus(id,val){

let e=document.getElementById(id);

if(!e)return;

e.innerHTML=val;

e.className=

(val==="ON" ||

val==="ONLINE")

?

"value on"

:

"value off";

}

function updateUI(data){

if(data.mode){

    document.getElementById(
        "modeStatus"
    ).innerHTML = data.mode;

}

document.getElementById(

"waterLevel"

).innerHTML=

data.water+"%";


document.getElementById(

"tankText"

).innerHTML=

data.water+"%";

document.getElementById(

"waterFill"

).style.height=

data.water+"%";

updateStatus(

"upStatus",

data.up

);

updateStatus(

"downStatus",

data.down

);

updateStatus(

"leftStatus",

data.left

);

updateStatus(

"rightStatus",

data.right

);

updateStatus(

"systemStatus",

data.system

);

document.getElementById(

"commandStatus"

).innerHTML=

data.command;

document.getElementById(

"ackStatus"

).innerHTML=

data.ack;

}

setInterval(()=>{

document.getElementById(

"clock"

).innerHTML=

new Date()

.toLocaleTimeString();

},1000);

const ctx=

document.getElementById(

"waterChart"

).getContext("2d");

const chart=new Chart(ctx,{

type:"line",

data:{

labels:[],

datasets:[{

label:"Water",

data:[],

borderColor:"#38bdf8"

}]

}

});

socket.on(

"mqtt_data",

(data)=>{

updateUI(data);

chart.data.labels.push(

new Date()

.toLocaleTimeString()

);

chart.data.datasets[0]

.data.push(

data.water || 0

);

if(

chart.data.labels.length>25

){

chart.data.labels.shift();

chart.data.datasets[0]

.data.shift();

}

chart.update();

}

);

document.querySelectorAll("button").forEach(btn=>{

btn.addEventListener(

"click",

function(){

document
.querySelectorAll("button")
.forEach(

b=>b.classList.remove(

"active-btn"

)

);

this.classList.add(

"active-btn"

);

}

);

});
function startJson(){

    fetch('/play_json')
    .then(res=>res.json())
    .then(data=>{

        log(data.status);

    });

}
function openBLE() {
    window.location.href = "/ble";
}
