/**
 * Join Meet Function v3 - uses seminar.sh for persistent profile
 */
const { spawn } = require('child_process');
const path = require('path');

const MEET_BOT_DIR = '/home/ubuntu/meet-bot';

function parseMeetRequest(text) {
  const meetRegex = /(https:\/\/meet\.google\.com\/[a-zA-Z0-9-]+)/i;
  const zoomRegex = /(https:\/\/[a-z0-9.]*zoom\.us\/j\/\d+)/i;
  const meetMatch = text.match(meetRegex);
  const zoomMatch = text.match(zoomRegex);
  const meetUrl = meetMatch ? meetMatch[1] : (zoomMatch ? zoomMatch[1] : null);
  
  let title = 'Manual Meeting';
  const titlePatterns = [
    /toplant[iı]s[iı]\s+['"](.+?)['"]/i,
    /['"](.+?)['"]\s+toplant[iı]/i,
  ];
  for (const p of titlePatterns) {
    const m = text.match(p);
    if (m) { title = m[1].trim(); break; }
  }
  return { meetUrl, title };
}

function joinMeeting(meetUrl, displayName = 'Sudenaz') {
  return new Promise((resolve) => {
    const child = spawn('bash', [
      path.join(MEET_BOT_DIR, 'seminar.sh'),
      meetUrl,
      displayName
    ], {
      cwd: MEET_BOT_DIR,
      detached: true,
      stdio: 'ignore',
      env: { ...process.env, DISPLAY: ':99' }
    });
    
    child.unref();
    
    setTimeout(() => {
      resolve({
        success: true,
        pid: child.pid,
        message: `✅ Bot başlatıldı!\n📹 Toplantı: ${meetUrl}\n👤 İsim: ${displayName}\n🎙️ Ses kaydı başlıyor...\n⏱️ Toplantı bitince otomatik transkript çıkarılacak.`,
        meetUrl,
        displayName
      });
    }, 1000);
  });
}

async function handleJoinMeet(args) {
  const { text, meetUrl: directUrl, displayName } = args;
  let meetUrl = directUrl;
  
  if (!meetUrl && text) {
    const parsed = parseMeetRequest(text);
    meetUrl = parsed.meetUrl;
  }
  
  if (!meetUrl) {
    return {
      success: false,
      message: '❌ Toplantı linki bulunamadı.\nÖrnek: `/join-meet https://meet.google.com/abc-defg-hij`\nZoom: `/join-meet https://zoom.us/j/123456789`'
    };
  }
  
  const result = await joinMeeting(meetUrl, displayName || 'Sudenaz');
  return result;
}

module.exports = { handleJoinMeet, joinMeeting, parseMeetRequest };

if (require.main === module) {
  const text = process.argv[2];
  if (!text) { console.error('Usage: node join_meet.js <url>'); process.exit(1); }
  handleJoinMeet({ text }).then(r => { console.log(JSON.stringify(r)); process.exit(r.success ? 0 : 1); });
}
