async function loadCameras(){

    const response=await fetch("/api/cameras");

    const cameras=await response.json();

    const grid=document.getElementById("camera-grid");

    if(!grid) return;

    grid.innerHTML="";

    cameras.forEach(camera=>{

        grid.innerHTML+=`

        <div class="camera-card">

            <div class="camera-top">

                <div>

                    <h3>${camera.name}</h3>

                    <p>${camera.location}</p>

                </div>

                <span class="${
                    camera.status==="ONLINE"
                    ?"camera-online"
                    :"camera-offline"
                }">

                    ● ${camera.status}

                </span>

            </div>

            ${
                camera.status==="ONLINE"

                ?

                `<img src="${camera.stream}">`

                :

                `<div class="camera-placeholder">

                    NO SIGNAL

                </div>`

            }

            <div class="camera-info">

                <div>

                    <span>Resolution</span>

                    <strong>${camera.resolution}</strong>

                </div>

                <div>

                    <span>FPS</span>

                    <strong>${camera.fps}</strong>

                </div>

                <div>

                    <span>AI</span>

                    <strong class="online-text">

                        ACTIVE

                    </strong>

                </div>

                <div>

                    <span>Status</span>

                    <strong>

                        ${camera.status}

                    </strong>

                </div>

            </div>

            <div class="camera-buttons">

                <a href="/camera/${camera.id}">

    <button class="live-btn">

        ▶ Live

    </button>

</a>

                <button class="snapshot-btn">

                    📷 Snapshot

                </button>

                <button class="refresh-btn">

                    ⟳ Refresh

                </button>

                <button class="settings-btn">

                    ⚙

                </button>

            </div>

        </div>

        `;

    });

}

loadCameras();