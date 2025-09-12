#!/bin/bash

# Azure Static Web Apps Deployment Script
# Make sure to set your deployment token as an environment variable:
# export AZURE_STATIC_WEB_APPS_DEPLOYMENT_TOKEN=your_token_here

set -e

echo "🚀 Building React application..."

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the application
echo "🔨 Building for production..."
npm run build

# Check if deployment token is set
if [ -z "$AZURE_STATIC_WEB_APPS_DEPLOYMENT_TOKEN" ]; then
    echo "❌ Error: AZURE_STATIC_WEB_APPS_DEPLOYMENT_TOKEN environment variable is not set"
    echo "Please set it with: export AZURE_STATIC_WEB_APPS_DEPLOYMENT_TOKEN=your_token_here"
    exit 1
fi

# Install Azure Static Web Apps CLI if not already installed
if ! command -v swa &> /dev/null; then
    echo "📥 Installing Azure Static Web Apps CLI..."
    npm install -g @azure/static-web-apps-cli
fi

# Deploy to Azure
echo "🌐 Deploying to Azure Static Web Apps..."
swa deploy dist --deployment-token $AZURE_STATIC_WEB_APPS_DEPLOYMENT_TOKEN

echo "✅ Deployment completed successfully!"
