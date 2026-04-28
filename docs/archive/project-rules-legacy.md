# Project Rules and Guidelines

## File Organization
- `/src/` - Source code files only
- `/docs/` - Documentation files only
- `/config/` - Configuration files only
- `/generated_files/` - Output from Onyx agents (do not modify manually)

## Development Guidelines
1. No temporary scripts should be committed to the main directories
2. All new features must have corresponding documentation
3. Configuration changes should be made thoughtfully and documented
4. Generated files should not be edited manually

## Maintenance Rules
1. Regular cleanup of temporary files and scripts
2. Verification that all components work together after changes
3. Backup of critical configuration before making changes
4. Testing of all MCP services after configuration updates

## Documentation Standards
1. All major components must have README documentation
2. API endpoints and usage patterns must be documented
3. Configuration parameters must be explained
4. Troubleshooting guides must be maintained

## Security Practices
1. API keys should never be hardcoded in scripts
2. Use environment variables for sensitive information
3. Regular rotation of API keys
4. Access control for sensitive configuration files