async function loadEvidence(){

    const response=await fetch("/api/evidence");

    const data=await response.json();

    const grid=document.getElementById("evidence-grid");

    grid.innerHTML="";

    data.evidence.forEach(file=>{

        grid.innerHTML+=`

        <div class="evidence-card">

            <img src="/evidence/${file}">

            <div class="evidence-info">

                <h3>${file}</h3>

                <p>

                    AI Captured Evidence

                </p>

                <div class="evidence-actions">

                    <button

                    class="view-btn"

                    onclick="window.open('/evidence/${file}')">

                    View

                    </button>

                    <a

                    href="/evidence/${file}"

                    download>

                    <button

                    class="download-btn">

                    Download

                    </button>

                    </a>

                    <button

                    class="delete-btn">

                    Delete

                    </button>

                </div>

            </div>

        </div>

        `;

    });

}

loadEvidence();

setInterval(loadEvidence,3000);