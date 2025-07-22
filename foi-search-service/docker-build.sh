#!/bin/bash

# foi-search-service Docker Build and Run Script
set -e

echo "🐳 FOI Search Service Docker Setup"
echo "========================"

# Function to display usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build      Build the Docker image"
    echo "  up         Start all services with docker-compose"
    echo "  down       Stop all services"
    echo "  logs       Show logs from all services"
    echo "  clean      Remove containers, networks, and volumes"
    echo "  rebuild    Clean, build, and start services"
    echo "  status     Show status of all services"
    echo ""
    exit 1
}

# Ensure .env file exists
ensure_env() {
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file from .env.docker template..."
        cp .env.docker .env
        echo "✅ Please review and update .env file with your configuration"
    fi
}

# Build Docker image
build() {
    echo "🔨 Building FOI Search Service Docker image..."
    docker build -t foi-search-service-api:latest .
    echo "✅ Build completed successfully!"
}

# Start services
up() {
    ensure_env
    echo "🚀 Starting FOI search services..."
    docker-compose up -d
    echo ""
    echo "✅ Services started successfully!"
    echo ""
    echo "📊 Service URLs:"
    echo "  • FOI Search Service API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Solr Admin: http://localhost:8983"
    echo ""
    echo "📝 View logs with: $0 logs"
}

# Stop services
down() {
    echo "🛑 Stopping FOI search services..."
    docker-compose down
    echo "✅ Services stopped successfully!"
}

# Show logs
logs() {
    echo "📋 Showing service logs..."
    docker-compose logs -f --tail=100
}

# Clean up everything
clean() {
    echo "🧹 Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo "✅ Cleanup completed!"
}

# Rebuild everything
rebuild() {
    echo "🔄 Rebuilding FOI Search Service..."
    clean
    build
    up
}

# Show service status
status() {
    echo "📊 Service Status:"
    echo "=================="
    docker-compose ps
    echo ""
    echo "🏥 Health Checks:"
    echo "=================="

    # Check API health
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ FOI Search Service API: Healthy"
    else
        echo "❌ FOI Search Service API: Unhealthy"
    fi

    # Check Solr health
    if curl -s http://localhost:8983/solr/admin/ping > /dev/null 2>&1; then
        echo "✅ Solr: Healthy"
    else
        echo "❌ Solr: Unhealthy"
    fi

}

# Main script logic
case "${1:-}" in
    build)
        build
        ;;
    up)
        up
        ;;
    down)
        down
        ;;
    logs)
        logs
        ;;
    clean)
        clean
        ;;
    rebuild)
        rebuild
        ;;
    status)
        status
        ;;
    *)
        usage
        ;;
esac