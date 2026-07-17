# Browser JavaScript Patterns for Voice Agent

## Audio Capture: MediaRecorder (Recommended)

`createScriptProcessor()` is deprecated in Chrome and crashes silently.
Always use `MediaRecorder` instead.

```javascript
// ✅ DO THIS — Modern, cross-browser
function startMic() {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });

        // Volume analyzer (optional visual feedback)
        const sourceNode = audioContext.createMediaStreamSource(mediaStream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        sourceNode.connect(analyser);

        // MediaRecorder for sending audio to server
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
            ? 'audio/webm;codecs=opus' : 'audio/webm';
        mediaRecorder = new MediaRecorder(mediaStream, { mimeType, audioBitsPerSecond: 32000 });

        mediaRecorder.ondataavailable = (e) => {
            if (ws && ws.readyState === WebSocket.OPEN && e.data.size > 0) {
                ws.send(e.data); // Blob sent to server WebSocket
            }
        };
        mediaRecorder.start(250); // Send chunk every 250ms

    } catch (e) {
        console.error('Mic start error:', e.name, e.message);
    }
}
```

## Error Handling

Always use try/catch with Turkish user-facing messages:

```javascript
try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
} catch (err) {
    const msg = err.name === 'NotAllowedError'
        ? '🚫 Mikrofon izni reddedildi!'
        : err.name === 'NotFoundError'
        ? '🎤 Mikrofon bulunamadı!'
        : 'Hata: ' + err.message;
    // Show to user, DON'T call disconnect()
    showError(msg);
    // Reset button so user can retry
    button.disabled = false;
    button.textContent = 'Tekrar Dene';
    return; // Important: return, don't disconnect
}
```

## WebSocket Test Page (No Audio)

For isolating WebSocket issues from audio issues, provide a test page that
only connects the WebSocket without touching the microphone:

```html
<!-- /test endpoint — pure WebSocket test -->
<script>
const ws = new WebSocket((location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + location.host + '/ws');
ws.onopen = () => log('✅ Connected, waiting...');
ws.onmessage = (e) => {
    if (typeof e.data === 'string') {
        const msg = JSON.parse(e.data);
        log('📥 ' + msg.type + ': ' + (msg.message || msg.description || ''));
    } else {
        log('📥 Binary: ' + e.data.size + ' bytes');
    }
};
ws.onclose = (ev) => log('🔌 Closed (code:' + ev.code + ' clean:' + ev.wasClean + ')');
</script>
```

## Common Browser Errors

| Error | Cause | Fix |
|---|---|---|
| `NotAllowedError` | User denied mic or non-HTTPS | Use cloudflared HTTPS tunnel |
| `NotFoundError` | No microphone found | Check device |
| WebSocket code 1006 | Cloudflared idle timeout or JS crash | Keep MediaRecorder sending chunks |
| Immediate onclose after onopen | `ScriptProcessorNode` crash | Switch to MediaRecorder |
