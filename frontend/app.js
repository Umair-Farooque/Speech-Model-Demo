// The library exports as LivekitClient, create LiveKit alias for compatibility
const LiveKit = typeof LivekitClient !== 'undefined' ? LivekitClient : undefined;

// Verify LiveKit is available (loaded from local file)
if (typeof LiveKit === 'undefined') {
    console.error('CRITICAL: LiveKit library not loaded!');
    alert('Error: LiveKit library failed to load. Please contact support.');
    throw new Error('LiveKit not available');
}

console.log('LiveKit library loaded successfully!', LiveKit);


const connectBtn = document.getElementById('connect-btn');
const statusText = document.getElementById('status-text');
const orb = document.getElementById('visualizer-orb');
const vitals = document.getElementById('vitals');
const latencyVal = document.getElementById('latency-val');

let room;
let isConnected = false;

async function connectToAgent() {
    try {
        statusText.innerText = "Requesting Access...";
        connectBtn.disabled = true;

        // Fetch token and LiveKit URL from our local server
        const response = await fetch('/token');
        if (!response.ok) {
            throw new Error(`Token request failed: ${response.statusText}`);
        }

        const data = await response.json();
        const token = data.token;
        const livekitUrl = data.url;

        statusText.innerText = "Connecting to LiveKit...";

        room = new LiveKit.Room({
            adaptiveStream: true,
            dynacast: true,
        });

        // Connect using the LiveKit URL from backend
        await room.connect(livekitUrl, token);

        isConnected = true;
        statusText.innerText = "Connected! Speak now...";
        vitals.classList.remove('hidden');
        connectBtn.innerText = "Disconnect";
        connectBtn.disabled = false;
        orb.classList.add('connected');

        // Setup Audio
        await room.localParticipant.setMicrophoneEnabled(true);

        room.on(LiveKit.RoomEvent.AudioPlaybackStatusChanged, () => {
            if (room.canPlaybackAudio) {
                statusText.innerText = "Ready to speak...";
            }
        });

        room.on(LiveKit.RoomEvent.TrackSubscribed, (track, publication, participant) => {
            if (track.kind === 'audio') {
                const element = track.attach();
                document.body.appendChild(element);
                statusText.innerText = "Agent is speaking...";
            }
        });

        room.on(LiveKit.RoomEvent.TrackUnsubscribed, (track) => {
            track.detach();
            statusText.innerText = "Listening...";
        });

        room.on(LiveKit.RoomEvent.Disconnected, (reason) => {
            handleDisconnect();
            if (reason) {
                statusText.innerText = `Disconnected: ${reason}`;
            }
        });

        // Visualization logic
        const interval = setInterval(() => {
            if (!room || room.state !== 'connected') {
                clearInterval(interval);
                return;
            }

            // Simple "speaking" detection based on participant audio levels
            const isSpeaking = Array.from(room.remoteParticipants.values()).some(p => p.isSpeaking) || room.localParticipant.isSpeaking;

            if (isSpeaking) {
                orb.classList.add('speaking');
            } else {
                orb.classList.remove('speaking');
            }
        }, 100);

    } catch (error) {
        console.error("Connection failed:", error);
        statusText.innerText = `Connection Failed: ${error.message}`;
        connectBtn.disabled = false;
        connectBtn.innerText = "Start Conversation";
        orb.classList.remove('connected');
    }
}

function handleDisconnect() {
    if (room) {
        room.disconnect();
        room = null;
    }
    isConnected = false;
    statusText.innerText = "Disconnected";
    vitals.classList.add('hidden');
    connectBtn.innerText = "Start Conversation";
    connectBtn.disabled = false;
    orb.classList.remove('connected', 'speaking');
}

connectBtn.addEventListener('click', () => {
    if (isConnected) {
        handleDisconnect();
    } else {
        connectToAgent();
    }
});

// Initialize UI - LiveKit is guaranteed to be loaded at this point
statusText.innerText = "Ready to start";
connectBtn.disabled = false;
connectBtn.innerText = "Start Conversation";

