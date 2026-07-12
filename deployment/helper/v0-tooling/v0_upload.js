const { v0 } = require('v0-sdk');
const fs = require('fs');
const path = require('path');

if (!process.env.V0_API_KEY) {
  console.error("Please set V0_API_KEY in your environment");
  process.exit(1);
}

function getFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  const stat = fs.statSync(dir);
  if (!stat.isDirectory()) {
    if (dir.match(/\.(ts|tsx|js|jsx|json|css|html|md)$/)) {
      fileList.push(dir);
    }
    return fileList;
  }
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filePath = path.join(dir, file);
    if (filePath.includes('src/components/ui') || filePath.includes('routeTree.gen.ts')) continue;
    if (fs.statSync(filePath).isDirectory()) {
      getFiles(filePath, fileList);
    } else {
      if (file.match(/\.(ts|tsx|js|jsx|json|css|html|md)$/)) {
        fileList.push(filePath);
      }
    }
  }
  return fileList;
}

async function main() {
  const prompt = fs.readFileSync('docs/ops/megaprompts/v0-dashboard-redesign-prompt.md', 'utf8');
  
  const potentialFiles = [
    'deployment/aisci-dashboard/package.json',
    'deployment/aisci-dashboard/tailwind.config.ts',
    'deployment/aisci-dashboard/tsconfig.json',
    'deployment/aisci-dashboard/vite.config.ts',
    'deployment/aisci-dashboard/index.html',
    'deployment/aisci-dashboard/src/start.ts',
    'deployment/aisci-dashboard/src/styles.css',
    'deployment/aisci-dashboard/src/router.tsx',
    'deployment/aisci-dashboard/src/routes/__root.tsx',
    'deployment/aisci-dashboard/src/routes/index.tsx',
    'deployment/aisci-dashboard/src/components/PageShell.tsx',
    'deployment/aisci-dashboard/src/components/layout/AppSidebar.tsx',
    'deployment/aisci-dashboard/src/components/layout/AppHeader.tsx'
  ];
  const filePaths = potentialFiles.filter(fp => fs.existsSync(fp));
  
  const files = filePaths.map(fp => {
    return {
      name: fp.replace('deployment/aisci-dashboard/', ''),
      content: fs.readFileSync(fp, 'utf8')
    };
  });
  
  console.log(`Gathered ${files.length} files. Initializing chat with v0...`);
  
  const chat = await v0.chats.init({
    type: 'files',
    files: files
  });

  console.log("Chat initialized:", chat.id);
  
  console.log("Sending prompt to chat...");
  const msgResponse = await v0.chats.sendMessage({
    chatId: chat.id,
    message: prompt,
    modelConfiguration: { modelId: 'v0-max' }
  });
  
  console.log("Response URL:", msgResponse.url || `https://v0.app/chat/${chat.id}`);
  console.log("Finished!");
}

main().catch(console.error);
