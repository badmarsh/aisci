const path = require('path');
const switchPath = path.join(process.cwd(), 'node_modules', '@base-ui/react', 'switch');
console.log("Switch package exists?", require('fs').existsSync(switchPath));
