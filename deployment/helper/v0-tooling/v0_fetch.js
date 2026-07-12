const { v0 } = require('v0-sdk');

if (!process.env.V0_API_KEY) {
  console.error("Please set V0_API_KEY in your environment");
  process.exit(1);
}

async function main() {
  const chatId = 'Z7D4l4sTesP';
  
  console.log("Fetching messages for chat", chatId);
  const msgs = await v0.chats.findMessages({ chatId });
  
  const assistantMsgs = msgs.items.filter(m => m.role === 'assistant');
  if (assistantMsgs.length === 0) {
    console.log("No assistant messages found yet. Maybe still generating?");
    return;
  }
  
  const latestMsg = assistantMsgs[0]; // Assuming newest-first or oldest-first? Let's print the length.
  console.log(`Found ${assistantMsgs.length} assistant messages.`);
  
  const lastMsg = assistantMsgs[assistantMsgs.length - 1];
  console.log("Latest message ID:", lastMsg.id);
  console.log("Content preview:", lastMsg.content?.substring(0, 500));
  
  // Try to write the content to a file to examine
  const fs = require('fs');
  fs.writeFileSync('v0_latest_msg.txt', JSON.stringify(lastMsg, null, 2));
  console.log("Wrote full message to v0_latest_msg.txt");
}

main().catch(console.error);
