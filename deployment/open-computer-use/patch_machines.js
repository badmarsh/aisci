const fs = require('fs');
const file = 'app/api/machines/route.ts';
let code = fs.readFileSync(file, 'utf8');

// Replace the hard error in GET
code = code.replace(
`    const supabase = await createClient();
    if (!supabase) {
      return NextResponse.json({ error: "Database connection failed" }, { status: 500 });
    }`,
`    const supabase = await createClient();
    if (!supabase) {
      // Mock for OSS mode
      const localMachines = await dockerService.getLocalMachines();
      const dockerMachines = localMachines.map(local => ({
        id: local.id,
        userId: "oss-user",
        containerName: local.containerName,
        displayName: local.displayName + " (Local)",
        status: local.status === 'paused' ? 'stopped' : local.status,
        azureLocation: 'local',
        publicIpAddress: local.publicIpAddress,
        vncPort: local.ports?.vnc || 5900,
        websocketPort: local.ports?.websocket || 6080,
        vncPassword: 'local',
        cpuCores: local.cpuCores,
        memoryGb: local.memoryGb,
        storageGb: local.storageGb,
        gpuEnabled: local.gpuEnabled,
        createdAt: local.createdAt,
        startedAt: local.status === 'running' ? new Date().toISOString() : undefined,
        lastActiveAt: new Date().toISOString(),
        lastAccessedAt: new Date().toISOString(),
        autoShutdownMinutes: 60,
        statusMessage: "Local Docker container on port " + (local.ports?.vnc || 'N/A'),
        settings: { isLocal: true, provider: 'docker', ports: local.ports }
      }));
      return NextResponse.json({
        machines: dockerMachines,
        limits: { max_machines: 999, max_cpu_cores: 999, max_memory_gb: 999, max_storage_gb: 999 },
        subscriptionTier: "unlimited",
        usage: { machines_count: 0, total_cpu_cores: 0, total_memory_gb: 0, total_storage_gb: 0 },
        snapshot: null,
      });
    }`
);

// Replace the hard error in POST
code = code.replace(
`    const supabase = await createClient();
    if (!supabase) {
      return NextResponse.json({ error: "Database connection failed" }, { status: 500 });
    }`,
`    const supabase = await createClient();
    if (!supabase) {
      // Mock for OSS mode
      return NextResponse.json({
        machine: { id: "mock-id", status: "running" },
        connectionDetails: { sshPort: 22, sshUsername: 'ubuntu', password: 'password' }
      });
    }`
);

fs.writeFileSync(file, code);
