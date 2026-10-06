let totalInterrogations = 0;
let activeSuspectName = "";
let suspectDeviceData = {};

// Handles switching tabs using the sidebar buttons
function showPage(pageId, buttonElement) {
    document.querySelectorAll(".page").forEach(function(section) { 
        section.classList.remove("active");
    });
   
    document.getElementById(pageId).classList.add("active");
    
    document.querySelectorAll(".nav-button").forEach(function(navButton) { 
        navButton.classList.remove("active");
    });
    
    buttonElement.classList.add("active");
}

// Queries your Python server to populate the interface elements
async function loadCaseData() {
    try {
        const suspectResponse = await fetch('/api/suspects');
        const suspects = await suspectResponse.json();
        
        const suspectGrid = document.getElementById('suspectGrid');
        const digitalSelect = document.getElementById('digitalSelect');
        const accusationSelect = document.getElementById('accusationSelect');
        
        if (suspectGrid) suspectGrid.innerHTML = '';
        if (digitalSelect) digitalSelect.innerHTML = '<option value="">Select a suspect</option>';
        if (accusationSelect) accusationSelect.innerHTML = '<option value="">Select Suspect</option>';
        
        const suspectCountDisplay = document.getElementById('suspectCount');
        if (suspectCountDisplay) suspectCountDisplay.innerText = suspects.length;

        suspects.forEach(suspect => {
            const name = suspect.SuspectNames || "Unknown Suspect";
            const age = suspect.Age || "Unknown";
            const profession = suspect.Professions || "Undocumented";
            const eyes = suspect.EyeColour || "Unknown";
            const hair = suspect.HairColour || "Unknown";
            const height = suspect.Height || "Unknown";

            if (suspectGrid) {
                const card = document.createElement('div');
                card.className = 'card';
                card.style.cssText = "background:#1f2937; padding:15px; margin-bottom:12px; border-left:4px solid #f59e0b; border-radius:4px; text-align:left; color:#fff;";
                card.innerHTML = `
                    <h3>${name} (Age: ${age})</h3>
                    <p style="color:#a1a1a6; font-size:0.9rem; margin-bottom:12px;">
                        Occupation: ${profession}<br>
                        Traits: ${height} tall, ${hair} hair, ${eyes} eyes
                    </p>
                    <button class="nav-button" style="background:#1e3a8a; color:white; padding:6px 12px; border:none; cursor:pointer; font-family:monospace; border-radius:4px;" onclick='executeInterrogation("${name}")'>
                        Interrogate Suspect
                    </button>
                `;
                suspectGrid.appendChild(card);
            }

            if (digitalSelect) {
                const optionOpt = document.createElement('option');
                optionOpt.value = name;
                optionOpt.innerText = name;
                digitalSelect.appendChild(optionOpt.cloneNode(true));
            }

            if (accusationSelect) {
                const optionOpt = document.createElement('option');
                optionOpt.value = name;
                optionOpt.innerText = name;
                accusationSelect.appendChild(optionOpt);
            }
        });

                const evidenceResponse = await fetch('/api/evidence');
        const clues = await evidenceResponse.json();
        
        const evidenceGrid = document.getElementById('evidenceGrid');
        if (evidenceGrid) evidenceGrid.innerHTML = '';
        
        const evidenceCountDisplay = document.getElementById('evidenceCount');
        if (evidenceCountDisplay) evidenceCountDisplay.innerText = clues.length;

        if (evidenceGrid) {
            if (clues.length === 0) {
                evidenceGrid.innerHTML = '<p style="color:#6b7280; padding:10px;">No records discovered yet. Begin interrogation logs to extract tracking lines.</p>';
            } else {
                clues.forEach(clue => {
                    const eKeys = Object.keys(clue);
                    const item = clue[eKeys] || "Forensic Entry Log Asset";
                    const mailHint = clue[eKeys] || "No relevant data traces.";
                    const searchHint = clue[eKeys] || "No query tracks.";
                    const noteHint = clue[eKeys] || "No text logs.";

                    const clueBox = document.createElement('div');
                    clueBox.style.cssText = "background:#1f2937; padding:15px; margin-bottom:12px; border-left:4px solid #10b981; border-radius:4px; text-align:left; width: 100%; box-sizing: border-box; color:#fff;";
                    clueBox.innerHTML = `
                        <h4 style="color:#10b981; margin:0 0 5px 0;">DISCOVERED: ${item}</h4>
                        <p style="font-size:0.85rem; line-height:1.5; color:#d1d5db; margin:5px 0 0 0;">
                            Mail Trace: ${mailHint}<br>
                            Web Search Trail: ${searchHint}<br>
                            Device Scrap: ${noteHint}
                        </p>
                    `;
                    evidenceGrid.appendChild(clueBox);
                });
            }
        }

    } catch (err) {
        console.error("Pipeline Sync Error: ", err);
    }
}

async function getDigitalEvidence() {
    const selectBox = document.getElementById('digitalSelect');
    const activeName = selectBox.value;
    const outputPanel = document.getElementById('digitalResults');
    
    if (!activeName) {
        if (outputPanel) outputPanel.innerHTML = '';
        return;
    }

    try {
        const response = await fetch('/api/footprint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: activeName })
        });
        const data = await response.json();

        if (data.success && outputPanel) {
            const logs = data.footprint;
            
            outputPanel.innerHTML = `
                <div style="margin-top:20px; display:grid; grid-template-columns:1fr 1fr; gap:15px; text-align:left;">
                    <div style="background:#161a22; padding:15px; border-top:3px solid #38bdf8; border-radius:4px;">
                        <h4 style="color:#38bdf8; margin-top:0;">Mail Invoices</h4>
                        <p style="font-size:0.9rem; font-style:italic; color:#fff;">${logs.email}</p>
                    </div>
                    <div style="background:#161a22; padding:15px; border-top:3px solid #38bdf8; border-radius:4px;">
                        <h4 style="color:#38bdf8; margin-top:0;">Local Note Entries</h4>
                        <p style="font-size:0.9rem; font-style:italic; color:#fff;">${logs.notes_app}</p>
                    </div>
                    <div style="background:#161a22; padding:15px; border-top:3px solid #a855f7; border-radius:4px;">
                        <h4 style="color:#a855f7; margin-top:0;">Bank History</h4>
                        <p style="font-size:0.9rem; font-style:italic; color:#fff;">${logs.bank_history}</p>
                    </div>
                    <div style="background:#161a22; padding:15px; border-top:3px solid #eab308; border-radius:4px;">
                        <h4 style="color:#eab308; margin-top:0;">Web Query History Cache</h4>
                        <ul style="padding-left:15px; margin:5px 0 0 0; font-size:0.9rem; color:#fff;">
                            ${logs.search_history.map(query => `<li style="margin-bottom:4px;">"\${query}"</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }
    } catch (err) {
        if (outputPanel) outputPanel.innerHTML = '<p style="color:#ef4444;">Failed to bypass network firewalls accessing hardware caches.</p>';
    }
}

async function executeInterrogation(suspectName) {
    try {
        const response = await fetch('/api/interrogate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: suspectName })
        });
        const outcomes = await response.json();
        
        if (outcomes.new_evidence_unlocked) {
            totalInterrogations++;
            const interrogationCountDisplay = document.getElementById('interrogationCount');
            if (interrogationCountDisplay) interrogationCountDisplay.innerText = totalInterrogations;
        }

        triggerCaseModal("Interrogation Terminal Output", outcomes.message);
        loadCaseData();

    } catch (err) {
        console.error(err);
    }
}

async function makeAccusation() {
    const selectBox = document.getElementById('accusationSelect');
    const suspectChoice = selectBox.value;
    
    if (!suspectChoice) {
        alert("Please pick an active suspect before submitting accusation metrics, detective.");
        return;
    }

    if (!confirm("Issue an absolute arrest warrant for " + suspectChoice + "? This choice is definitive.")) return;

    try {
        const response = await fetch('/api/accuse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: suspectChoice })
        });
        const result = await response.json();
        
        document.body.innerHTML = `
            <div style="max-width:650px; margin:120px auto; padding:40px; background:#161a22; border:2px solid ${result.status === 'victory' ? '#10b981' : '#ef4444'}; text-align:center; border-radius:8px; box-shadow:0 10px 25px rgba(0,0,0,0.5);">
                <h1 style="color:${result.status === 'victory' ? '#10b981' : '#ef4444'}; font-family:monospace; margin-top:0;">${result.title}</h1>
                <p style="font-size:1.15rem; line-height:1.6; margin-top:20px; font-family:monospace; color:#d1d5db; text-align:left; background:#0d0e12; padding:20px; border-radius:4px; border:1px solid #333;">${result.message}</p>
                <br>
                <button onclick="window.location.reload()" style="padding:10px 25px; font-family:monospace; font-weight:bold; background:#374151; color:white; border:none; cursor:pointer; border-radius:4px;">
                    Restart Session
                </button>
            </div>
        `;
    } catch (err) {
        alert("Error communicating accusation warrant back down to Python server loops.");
    }
}

function triggerCaseModal(title, bodyText) {
    const modalTitle = document.getElementById('modualTitle');
    const modalBody = document.getElementById('modualBody');
    if (modalTitle) modalTitle.innerText = title;
    if (modalBody) modalBody.innerText = bodyText;
    
    const modalElement = document.getElementById('modual');
    if (modalElement) {
        modalElement.style.display = 'block';
        modalElement.style.position = 'fixed';
        modalElement.style.zIndex = '999';
        modalElement.style.left = '0';
        modalElement.style.top = '0';
        modalElement.style.width = '100%';
        modalElement.style.height = '100%';
        modalElement.style.backgroundColor = 'rgba(0,0,0,0.75)';
        
        const contentBox = modalElement.querySelector('.modual-content');
        if (contentBox) {
            contentBox.style.cssText = "background:#161a22; color:#fff; border:1px solid #ff5555; max-width:500px; margin:15% auto; padding:20px; border-radius:4px; position:relative; text-align:left;";
            const closeBtn = contentBox.querySelector('.close');
            if (closeBtn) closeBtn.style.cssText = "position:absolute; right:15px; top:10px; background:none; border:none; color:#a1a1a6; font-size:1.3rem; cursor:pointer;";
        }
    }
}

function closeModual() {
    const modalElement = document.getElementById('modual');
    if (modalElement) modalElement.style.display = 'none';
}

window.onload = loadCaseData;
