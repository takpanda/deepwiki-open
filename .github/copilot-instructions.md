# DeepWiki-Open Developer Instructions

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

DeepWiki-Open is a hybrid Next.js frontend + Python FastAPI backend application that generates AI-powered documentation from code repositories.

### Critical Network Dependency Limitations

**IMPORTANT**: This application has strict internet connectivity requirements that prevent it from running in network-restricted environments:

- **Frontend Build**: Requires access to `fonts.googleapis.com` for Google Fonts
- **Backend Startup**: Requires access to `openaipublic.blob.core.windows.net` for tiktoken encoding downloads
- **Docker Build**: Requires access to Node.js GPG keys and various package registries

### Bootstrap and Dependencies

#### Frontend Dependencies
```bash
# Option 1: npm (recommended for speed)
npm install

# Option 2: yarn (used in project documentation)
yarn install
```
**Timing**: npm ~4 seconds, yarn ~48 seconds. NEVER CANCEL - wait for completion.

#### Backend Dependencies  
```bash
# Install Python dependencies
pip3 install -r api/requirements.txt
```
**Timing**: Takes approximately 35 seconds. NEVER CANCEL - wait for completion.

**Alternative with uv** (if available):
```bash
uv sync
```

### Development Environment Setup

#### Frontend Development
```bash
# Start frontend development server
npm run dev
# or
yarn dev
```
- **Port**: 3000
- **URL**: http://localhost:3000
- **Timing**: Ready in ~1 second after dependencies are installed
- **Works without backend**: Yes - shows UI with backend connection errors

#### Backend Development
```bash
# Create minimal .env file (required)
echo "GOOGLE_API_KEY=your_google_api_key" > .env
echo "OPENAI_API_KEY=your_openai_api_key" >> .env

# Start backend API server
python3 -m api.main --port 8001
```
- **Port**: 8001 (configurable via PORT environment variable)
- **Network Requirements**: CRITICAL - requires internet access for tiktoken downloads
- **Environment Variables**: GOOGLE_API_KEY and OPENAI_API_KEY are required

### Building and Testing

#### Frontend Build
```bash
npm run build
# or
yarn build
```
**CRITICAL LIMITATION**: Build fails in network-restricted environments due to Google Fonts dependency.

**Workaround for Network-Restricted Environments**:
1. Comment out Google Fonts imports in `src/app/layout.tsx`:
   ```typescript
   // import { Noto_Sans_JP, Noto_Serif_JP, Geist_Mono } from "next/font/google";
   ```
2. Remove font variables from className
3. Build takes ~48 seconds when successful. NEVER CANCEL - set timeout to 60+ minutes.

#### Frontend Linting
```bash
npm run lint
# or
yarn lint
```
**Timing**: Takes ~3 seconds. Always run before committing.

#### Python Testing
```bash
python3 -m pytest test/ -v
```
**CRITICAL LIMITATION**: Tests fail in network-restricted environments due to tiktoken download requirements.

### Docker

#### Docker Build
```bash
docker build -t deepwiki-open .
```
**CRITICAL LIMITATION**: Docker build fails in network-restricted environments due to:
- Node.js GPG key download requirements
- Various package registry access needs

#### Docker Compose
```bash
docker-compose up
```
Requires `.env` file with API keys.

### Project Structure

#### Key Directories
- **`src/`**: Next.js frontend source code
- **`api/`**: Python FastAPI backend source code
- **`api/config/`**: JSON configuration files for models and settings
- **`test/`**: Python test files
- **`public/`**: Static frontend assets

#### Configuration Files
- **`package.json`**: Frontend dependencies and scripts
- **`pyproject.toml`**: Python project configuration
- **`api/requirements.txt`**: Python dependencies
- **`next.config.ts`**: Next.js configuration with API proxying
- **`eslint.config.mjs`**: ESLint configuration

### Environment Variables

#### Required for Full Functionality
```bash
GOOGLE_API_KEY=your_google_api_key        # Required for Google Gemini models
OPENAI_API_KEY=your_openai_api_key        # Required for embeddings and OpenAI models
```

#### Optional
```bash
OPENROUTER_API_KEY=your_openrouter_api_key  # For OpenRouter models
AWS_ACCESS_KEY_ID=your_aws_access_key_id    # For AWS Bedrock models
AWS_SECRET_ACCESS_KEY=your_aws_secret_key   # For AWS Bedrock models
AWS_REGION=us-east-1                        # AWS region
DEEPWIKI_CONFIG_DIR=path/to/config          # Custom config directory
PORT=8001                                   # Backend port (default: 8001)
```

### Validation and Testing

#### Manual Validation Scenarios
After making changes, always test these scenarios:

1. **Frontend-Only Validation** (works in network-restricted environments):
   ```bash
   npm run dev  # or yarn dev
   # Navigate to http://localhost:3000
   # Verify UI loads and displays properly
   # Check browser console for errors (backend connection errors are expected)
   ```

2. **Full Stack Validation** (requires internet access):
   ```bash
   # Terminal 1: Start backend
   python3 -m api.main --port 8001
   
   # Terminal 2: Start frontend  
   npm run dev  # or yarn dev
   
   # Navigate to http://localhost:3000
   # Test repository URL input and wiki generation
   ```

#### Pre-Commit Validation
Always run these commands before committing:
```bash
npm run lint                 # Frontend linting (~3 seconds)
# or
yarn lint                    # Frontend linting (~3 seconds)
# Note: Python tests require network access and may fail in restricted environments
```

### Common Issues and Solutions

#### "Failed to fetch Google Fonts" 
- **Cause**: Network restrictions blocking fonts.googleapis.com
- **Solution**: Use the font import workaround described in the Building section

#### "Failed to resolve openaipublic.blob.core.windows.net"
- **Cause**: Network restrictions blocking tiktoken downloads  
- **Solution**: This is a fundamental limitation - backend cannot start without internet access

#### Build Timeouts
- **Always set timeouts of 60+ minutes** for build commands
- **NEVER CANCEL** builds or long-running commands
- Frontend build: ~48 seconds, Backend dependency install: ~35 seconds

### Performance Notes
- **Frontend development server**: Ready in ~1 second
- **Frontend build**: ~48 seconds (when network is available)
- **Backend startup**: Depends on network access for initial tiktoken download
- **Dependency installation**: npm ~4s, yarn ~48s, Backend ~35s

### Technology Stack
- **Frontend**: Next.js 15.3.1, TypeScript, React 19, Tailwind CSS
- **Backend**: Python 3.12+, FastAPI, uvicorn
- **AI/ML**: Google Generative AI, OpenAI, tiktoken, adalflow, faiss
- **Package Managers**: yarn (frontend), pip/uv (backend)
- **Deployment**: Docker, docker-compose

### Working in Network-Restricted Environments

In environments with limited internet access:
1. **✅ Frontend development works** with font import workaround
2. **❌ Frontend build fails** without Google Fonts workaround  
3. **❌ Backend startup fails** due to tiktoken requirements
4. **❌ Python tests fail** due to network dependencies
5. **❌ Docker build fails** due to various network requirements

For development in such environments, focus on frontend-only changes and use the font workaround.