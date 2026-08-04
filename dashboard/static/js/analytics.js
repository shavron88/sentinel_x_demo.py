let incidentChart;

let pieChart;

async function loadAnalytics(){

    try{

        const response = await fetch("/analytics_data");

        const data = await response.json();

        document.getElementById("total-incidents").innerText=data.total;

        document.getElementById("people-count").innerText=data.people;

        document.getElementById("vehicle-count").innerText=data.vehicles;

        document.getElementById("analytics-threat").innerText=data.threat;

        drawLine(data);

        drawPie(data);

        drawTable(data.events);

    }

    catch(e){

        console.log(e);

    }

}

function drawLine(data){

    const ctx=document.getElementById("incidentChart");

    if(incidentChart){

        incidentChart.destroy();

    }

    incidentChart=new Chart(ctx,{

        type:"line",

        data:{

            labels:data.labels,

            datasets:[{

                label:"Incidents",

                data:data.values,

                borderWidth:3,

                tension:.4

            }]

        }

    });

}

function drawPie(data){

    const ctx=document.getElementById("pieChart");

    if(pieChart){

        pieChart.destroy();

    }

    pieChart=new Chart(ctx,{

        type:"pie",

        data:{

            labels:["Persons","Vehicles","Falls","Weapons"],

            datasets:[{

                data:[

                    data.people,

                    data.vehicles,

                    data.falls,

                    data.weapons

                ]

            }]

        }

    });

}

function drawTable(events){

    const table=document.getElementById("analytics-table");

    table.innerHTML="";

    events.forEach(e=>{

        table.innerHTML+=`

        <div class="analytics-row">

            <span>${e.event}</span>

            <span>${e.time}</span>

            <span>${e.severity}</span>

        </div>

        `;

    });

}

loadAnalytics();

setInterval(loadAnalytics,5000);