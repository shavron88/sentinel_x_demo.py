let allIncidents=[];

async function loadIncidents(){

    const response=await fetch("/api/incidents");

    allIncidents=await response.json();

    renderIncidents(allIncidents);

}

function renderIncidents(data){

    const list=document.getElementById("incident-list");

    list.innerHTML="";

    data.forEach(item=>{

        list.innerHTML+=`

        <div class="incident-card ${item.severity.toLowerCase()}">

            <div class="incident-header">

                <h3>${item.type}</h3>

                <strong>${item.severity}</strong>

            </div>

            <div class="incident-meta">

                <span>📍 ${item.zone}</span>

                <span>🕒 ${item.time}</span>

            </div>

            <div class="incident-description">

                ${item.description}

            </div>

            <button class="view-btn">

                View Evidence

            </button>

        </div>

        `;

    });

}

document.querySelectorAll(".filter-btn").forEach(btn=>{

    btn.addEventListener("click",()=>{

        document.querySelectorAll(".filter-btn")

                .forEach(b=>b.classList.remove("active"));

        btn.classList.add("active");

        const filter=btn.dataset.filter;

        if(filter==="ALL"){

            renderIncidents(allIncidents);

        } else {

            renderIncidents(

                allIncidents.filter(i=>i.severity===filter)

            );

        }

    });

});

document.getElementById("incident-search")

        .addEventListener("input",e=>{

    const q=e.target.value.toLowerCase();

    renderIncidents(

        allIncidents.filter(i=>

            i.type.toLowerCase().includes(q) ||

            i.zone.toLowerCase().includes(q) ||

            i.description.toLowerCase().includes(q)

        )

    );

});

loadIncidents();