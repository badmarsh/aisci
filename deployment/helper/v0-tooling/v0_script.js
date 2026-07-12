const { v0 } = require('v0-sdk');
const fs = require('fs');

async function main() {
  if (!process.env.V0_API_KEY) {
    console.error("Please set V0_API_KEY in your environment");
    process.exit(1);
  }
  
  const prompt = fs.readFileSync('docs/ops/megaprompts/v0-dashboard-redesign-prompt.md', 'utf8');
  
  console.log("Initializing chat with v0...");
  const chat = await v0.chats.init({
    type: 'repo',
    repo: {
      url: 'https://github.com/badmarsh/aisci',
      branch: 'main'
    }
  });

  console.log("Chat initialized:", chat.id);
  
  console.log("Sending prompt to chat...");
  const msgResponse = await v0.chats.sendMessage({
    chatId: chat.id,
    message: prompt,
    modelConfiguration: { modelId: 'v0-max' }
  });
  
  console.log("Response:", msgResponse);
}

main().catch(console.error);
