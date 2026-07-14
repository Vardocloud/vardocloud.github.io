/**
 * Cancel Meet Function
 * Handles meeting cancellation requests from Vanitas/Hermes
 */

const { spawn } = require('child_process');
const path = require('path');

const MEET_BOT_DIR = '/home/ubuntu/meet-bot';

/**
 * Cancel a meeting by identifier
 */
function cancelMeet(identifier) {
  return new Promise((resolve, reject) => {
    const cancel = spawn('node', [
      path.join(MEET_BOT_DIR, 'cancel-meet.js'),
      identifier
    ], {
      cwd: MEET_BOT_DIR,
      stdio: 'pipe'
    });
    
    let output = '';
    let error = '';
    
    cancel.stdout.on('data', d => { output += d.toString(); });
    cancel.stderr.on('data', d => { error += d.toString(); });
    
    cancel.on('close', code => {
      if (code === 0) {
        resolve({
          success: true,
          message: `Toplantı iptal edildi: ${identifier}`,
          output: output.trim()
        });
      } else {
        resolve({
          success: false,
          message: `İptal edilemedi: ${identifier}`,
          error: error.trim() || output.trim()
        });
      }
    });
  });
}

/**
 * Parse natural language cancellation request
 */
function parseCancelRequest(text) {
  // Extract identifier (number, title, or id)
  const patterns = [
    /#?(\d+)/,  // Number like #1 or 1
    /['"](.+?)['"]/,  // Quoted text
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      return match[1];
    }
  }
  
  // If no specific identifier, return the whole text as fallback
  return text.replace(/iptal|et|vazgeç|cancel/gi, '').trim();
}

/**
 * Main handler for Hermes skill
 */
async function handleCancelMeet(args) {
  const { text, identifier: directId } = args;
  
  let identifier = directId;
  
  if (!identifier && text) {
    identifier = parseCancelRequest(text);
  }
  
  if (!identifier) {
    return {
      success: false,
      message: 'İptal edilecek toplantı belirtilmedi. Örnek: "1. toplantıyı iptal et" veya "bardo toplantısını iptal et"',
      example: '/join-meet-cancel #1'
    };
  }
  
  const result = await cancelMeet(identifier);
  return result;
}

module.exports = { handleCancelMeet, cancelMeet, parseCancelRequest };

// CLI usage
if (require.main === module) {
  const identifier = process.argv[2];
  if (!identifier) {
    console.error('Usage: node cancel_meet.js <meeting-id|#number|title>');
    process.exit(1);
  }
  
  handleCancelMeet({ identifier }).then(result => {
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.success ? 0 : 1);
  });
}
