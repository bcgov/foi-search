@echo off
setlocal enabledelayedexpansion

REM FOI Search Service Docker Build and Run Script for Windows

echo 🐳 FOI Search Service Docker Setup
echo ========================

REM Display usage instructions
:usage
if "%1"=="usage" (
    echo Usage: docker-build.bat [COMMAND]
    echo.
    echo Commands:
    echo   build      Build the Docker image
    echo   up         Start all services with docker-compose
    echo   down       Stop all services
    echo   logs       Show logs from all services
    echo   clean      Remove containers, networks, and volumes
    echo   rebuild    Clean, build, and start services
    echo   status     Show status of all services
    goto :eof
)

REM Ensure .env file exists
if not exist ".env" (
    echo 📝 Creating .env file from .env.docker template...
    copy .env.docker .env > nul
    echo ✅ Please review and update .env file with your configuration
)

REM Parse the command
if "%1"=="build" (
    echo 🔨 Building FOI Search Service Docker image...
    docker build -t foi-search-service-api:latest .
    echo ✅ Build completed successfully!
    goto :eof
)

if "%1"=="up" (
    echo 🚀 Starting FOI search services...
    docker-compose up -d
    echo.
    echo ✅ Services started successfully!
    echo.
    echo 📊 Service URLs:
    echo   • FOI Search Service API: http://localhost:8000
    echo   • API Docs: http://localhost:8000/docs
    echo   • Solr Admin: http://localhost:8983
    echo.
    echo 📝 View logs with: docker-build.bat logs
    goto :eof
)

if "%1"=="down" (
    echo 🛑 Stopping FOI search services...
    docker-compose down
    echo ✅ Services stopped successfully!
    goto :eof
)

if "%1"=="logs" (
    echo 📋 Showing service logs...
    docker-compose logs -f --tail=100
    goto :eof
)

if "%1"=="clean" (
    echo 🧹 Cleaning up Docker resources...
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo ✅ Cleanup completed!
    goto :eof
)

if "%1"=="rebuild" (
    call "%~f0" clean
    call "%~f0" build
    call "%~f0" up
    goto :eof
)

if "%1"=="status" (
    echo 📊 Service Status:
    docker-compose ps
    echo.
    echo 🏥 Health Checks:

    REM Check FOI API
    curl -s http://localhost:8000/health >nul
    if %errorlevel%==0 (
        echo ✅ FOI Search Service API: Healthy
    ) else (
        echo ❌ FOI Search Service API: Unhealthy
    )

    REM Check Solr
    curl -s http://localhost:8983/solr/admin/ping >nul
    if %errorlevel%==0 (
        echo ✅ Solr: Healthy
    ) else (
        echo ❌ Solr: Unhealthy
    )

    goto :eof

)

REM If no valid command, show usage
call :usage
