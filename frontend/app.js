// Configuration
const API_BASE = window.location.origin; // Dynamically uses current host/port
let currentUserCoords = { lat: null, lon: null };

// DOM Elements
const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const locSelector = document.getElementById('simulated-location');
const currentCoordsEl = document.getElementById('current-coords');
const nearestLandmarkEl = document.getElementById('nearest-landmark');
const monumentsContainer = document.getElementById('monuments-container');

// --- Initialization ---
function init() {
    setupEventListeners();
    getLocation(); // Try real GPS first
}

function setupEventListeners() {
    // Chat Interactions
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    // Location Simulation
    locSelector.addEventListener('change', (e) => {
        if (e.target.value) {
            const [lat, lon] = e.target.value.split(',').map(Number);
            updateLocation(lat, lon, true);
        } else {
            getLocation(); // Revert to real GPS
        }
    });

    // Refresh Location Button
    document.getElementById('refresh-location').addEventListener('click', getLocation);
    
    // Modal Close
    document.querySelector('.close-modal').addEventListener('click', () => {
        document.getElementById('monument-modal').classList.add('hidden');
    });
}

// --- Location Logic ---
function getLocation() {
    currentCoordsEl.textContent = "Locating...";
    
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            updateLocation(position.coords.latitude, position.coords.longitude);
        },
        () => {
            currentCoordsEl.textContent = "Location Denied";
            alert("Please enable location services or use the simulator dropdown.");
        }
    );
}

function updateLocation(lat, lon, isSimulated = false) {
    currentUserCoords = { lat, lon };
    currentCoordsEl.textContent = `${lat.toFixed(4)}, ${lon.toFixed(4)} ${isSimulated ? '(Simulated)' : ''}`;
    
    // Update Context (Nearest Monument)
    fetchNearbyMonuments(lat, lon);
}

// --- API Interactions ---
async function fetchNearbyMonuments(lat, lon) {
    try {
        const response = await fetch(`${API_BASE}/api/check-location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lon, radius_km: 2.0 })
        });
        
        const data = await response.json();
        
        if (data.success && data.monuments.length > 0) {
            renderMonuments(data.monuments);
            nearestLandmarkEl.textContent = data.monuments[0].name;
            nearestLandmarkEl.classList.remove('highlight'); // Reset animation/style if needed
        } else {
            monumentsContainer.innerHTML = '<div class="placeholder-msg">No monuments found nearby.</div>';
            nearestLandmarkEl.textContent = "No Landmarks Nearby";
        }
    } catch (error) {
        console.error('Error fetching monuments:', error);
    }
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text || !currentUserCoords.lat) return;

    // UI Updates
    addMessage(text, 'user');
    userInput.value = '';
    
    // Loading State
    const loadingId = addMessage('Thinking...', 'bot', true);

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_message: text,
                user_latitude: currentUserCoords.lat,
                user_longitude: currentUserCoords.lon
            })
        });

        const data = await response.json();
        
        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) loadingMsg.remove();

        if (data.success) {
            addMessage(data.response, 'bot');
        } else {
            addMessage("Sorry, I'm having trouble connecting right now.", 'bot');
        }

    } catch (error) {
        console.error('Chat error:', error);
        addMessage("Network error. Please try again.", 'bot');
    }
}

async function getSafetyTips() {
    if(!currentUserCoords.lat) return alert("Location not found yet.");
    
    try {
        const response = await fetch(`${API_BASE}/api/safety-tips`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                latitude: currentUserCoords.lat, 
                longitude: currentUserCoords.lon 
            })
        });
        
        const data = await response.json();
        const tipsHtml = `
            <strong>Safety Tips:</strong><br>
            <ul>${data.safety_tips.map(t => `<li>${t}</li>`).join('')}</ul>
            <br>
            <strong>Emergency:</strong> Police: ${data.emergency_contacts.police}
        `;
        addMessage(tipsHtml, 'bot'); // Send as chat message for simplicity
        
    } catch (e) {
        console.error(e);
    }
}

// --- UI Helpers ---
function addMessage(text, sender, isLoading = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    if (isLoading) msgDiv.id = `msg-${Date.now()}`;
    
    msgDiv.innerHTML = `
        <div class="avatar"><i class="fa-solid fa-${sender === 'bot' ? 'robot' : 'user'}"></i></div>
        <div class="text">${text}</div>
    `;
    
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return msgDiv.id;
}

function renderMonuments(monuments) {
    monumentsContainer.innerHTML = '';
    monuments.forEach(m => {
        const card = document.createElement('div');
        card.className = 'monument-card';
        card.innerHTML = `
            <div class="monument-top">
                <span class="monument-name">${m.name}</span>
                <span class="monument-dist">${m.distance_km} km</span>
            </div>
            <span class="monument-category">${m.category}</span>
        `;
        card.onclick = () => showMonumentModal(m);
        monumentsContainer.appendChild(card);
    });
}

function showMonumentModal(monument) {
    document.getElementById('modal-title').textContent = monument.name;
    document.getElementById('modal-desc').textContent = monument.description;
    document.getElementById('modal-timings').textContent = monument.opening_hours;
    document.getElementById('modal-price').textContent = `₹${monument.pricing.indian} (Indian)`;
    document.getElementById('monument-modal').classList.remove('hidden');
    
    // Play Audio (Synthetic implementation for demo)
    const playBtn = document.getElementById('play-audio-btn');
    playBtn.onclick = () => {
        const utterance = new SpeechSynthesisUtterance(monument.audio_script);
        window.speechSynthesis.speak(utterance);
    };
}

// Start App
init();
