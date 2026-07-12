const { v0 } = require('v0-sdk');
const fs = require('fs');

if (!process.env.V0_API_KEY) {
  console.error("Please set V0_API_KEY in your environment");
  process.exit(1);
}

async function main() {
  const prompt = fs.readFileSync('docs/ops/megaprompts/v0-dashboard-redesign-prompt.md', 'utf8');
  
  const targetFiles = [
    'deployment/aisci-dashboard/package.json',
    'deployment/aisci-dashboard/vite.config.ts',
    'deployment/aisci-dashboard/tsconfig.json',
    'deployment/aisci-dashboard/index.html',
    'deployment/aisci-dashboard/src/main.tsx',
    'deployment/aisci-dashboard/src/index.css',
    'deployment/aisci-dashboard/src/routeTree.gen.ts',
    'deployment/aisci-dashboard/src/routes/__root.tsx',
    'deployment/aisci-dashboard/src/routes/index.tsx'
  ];
  
  const files = [];
  for (const fp of targetFiles) {
    if (fs.existsSync(fp)) {
      files.push({
        name: fp.replace('deployment/aisci-dashboard/', ''),
        content: fs.readFileSync(fp, 'utf8')
      });
    }
  }
  
  console.log(`Gathered ${files.length} files. Initializing chat with v0...`);
  
  const chat = await v0.chats.init({
    type: 'files',
    files: files
  });

  console.log("Chat initialized:", chat.id);
  console.log("Chat URL:", `https://v0.app/chat/${chat.id}`);
  
  console.log("Sending prompt to chat...");
  const msgResponse = await v0.chats.sendMessage({
    chatId: chat.id,
    messages: [{ role: 'user', content: prompt }],
    modelConfiguration: { modelId: 'v0-max' }
  });
  
  console.log("Finished! Check the chat at the URL above!");
}

main().catch(console.error);
