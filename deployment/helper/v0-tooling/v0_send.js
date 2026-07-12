const { v0 } = require('v0-sdk');
const fs = require('fs');

if (!process.env.V0_API_KEY) {
  console.error("Please set V0_API_KEY in your environment");
  process.exit(1);
}

async function main() {
  const prompt = fs.readFileSync('docs/ops/megaprompts/v0-dashboard-redesign-prompt.md', 'utf8');
  const chatId = 'Z7D4l4sTesP';
  
  console.log("Sending prompt to chat", chatId, "...");
  const msgResponse = await v0.chats.sendMessage({
    chatId: chatId,
    message: prompt,
    modelConfiguration: { modelId: 'v0-max' }
  });
  
  console.log("Finished! Check the chat at: https://v0.app/chat/" + chatId);
}

main().catch(console.error);
