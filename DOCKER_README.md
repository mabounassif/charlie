# Docker Setup for Chess Opening Recommendation System

This project includes Docker configuration for both development and production deployment on Railway.

## 🐳 Docker Configuration

### Production Dockerfile
The `Dockerfile` is configured for Railway deployment with:
- Ubuntu 22.04 base image with Stockfish pre-installed
- Python 3 with all required dependencies
- Non-root user for security
- Web application interface for easy access

### Development Container
The `.devcontainer/devcontainer.json` references the same Dockerfile for consistent development environments.

## 🚀 Railway Deployment

### Prerequisites
1. Railway account
2. Git repository connected to Railway
3. Railway CLI (optional)

### Deployment Steps
1. **Connect to Railway**: Link your GitHub repository to Railway
2. **Automatic Detection**: Railway will detect the Dockerfile and build automatically
3. **Environment Variables**: Configure any needed environment variables in Railway dashboard
4. **Deploy**: Railway will build and deploy your application

### Configuration Files
- `Dockerfile`: Production container configuration
- `railway.toml`: Railway-specific deployment settings
- `.dockerignore`: Optimizes build context
- `src/web_app.py`: Web interface for the chess analysis system

## 🛠️ Local Development

### Using DevContainer
1. Install VS Code with Dev Containers extension
2. Open the project in VS Code
3. When prompted, click "Reopen in Container"
4. The development environment will be set up automatically

### Manual Docker Build
```bash
# Build the image
docker build -t chess-recommender .

# Run the container
docker run -p 8000:8000 chess-recommender

# Access the web interface
open http://localhost:8000
```

## 🌐 Web Interface

The web application provides:
- **File Upload**: Upload PGN files for analysis
- **Real-time Analysis**: Process games with Stockfish engine
- **Results Display**: View analysis results and recommendations
- **Health Check**: `/health` endpoint for monitoring

## 📁 File Structure

```
.
├── Dockerfile              # Production container
├── .dockerignore          # Build optimization
├── railway.toml           # Railway configuration
├── .devcontainer/         # Development container config
│   └── devcontainer.json
├── src/
│   ├── main.py           # CLI application
│   └── web_app.py        # Web application
└── requirements.txt       # Python dependencies
```

## 🔧 Customization

### Environment Variables
- `PORT`: Web server port (default: 8000)
- `PYTHONUNBUFFERED`: Python output buffering
- `STOCKFISH_PATH`: Custom Stockfish engine path

### Adding Dependencies
1. Update `requirements.txt` for Python packages
2. Modify `Dockerfile` for system packages
3. Rebuild the container

## 🚨 Troubleshooting

### Common Issues
1. **Stockfish not found**: Ensure Stockfish is installed in the container
2. **Port conflicts**: Change the exposed port in Dockerfile
3. **Memory issues**: Increase Railway memory allocation
4. **Build failures**: Check `.dockerignore` excludes

### Debug Commands
```bash
# Check container logs
docker logs <container_id>

# Enter running container
docker exec -it <container_id> /bin/bash

# Test Stockfish installation
docker exec <container_id> stockfish --version
```

## 📊 Monitoring

The application includes:
- Health check endpoint at `/health`
- Logging to stdout/stderr
- Error handling and reporting
- Performance monitoring capabilities

For Railway-specific monitoring, check the Railway dashboard for logs and metrics. 