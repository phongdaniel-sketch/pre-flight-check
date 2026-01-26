#!/bin/bash

# Deployment Manager Script for Vercel

echo "=================================================="
echo "   PRE-FLIGHT CHECK - DEPLOYMENT MANAGER"
echo "=================================================="
echo ""

# Function to check git status
check_git_status() {
    if [[ -n $(git status -s) ]]; then
        echo "⚠️  You have uncommitted changes."
        read -p "Do you want to commit them now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter commit message: " commit_msg
            git add .
            git commit -m "$commit_msg"
            echo "✅ Changes committed."
        else
            echo "Continuing without committing..."
        fi
    fi
}

echo "Which environment do you want to deploy to?"
echo "  1) Staging (develop branch)"
echo "  2) Production (main branch)"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Preparing STAGING deployment..."
        
        # Ensure we are on develop
        current_branch=$(git symbolic-ref --short HEAD)
        if [[ "$current_branch" != "develop" ]]; then
            echo "Switching to develop branch..."
            git checkout develop || exit 1
        fi
        
        check_git_status
        
        echo "Pushing to origin/develop..."
        git push origin develop
        
        echo ""
        echo "Deploying to Vercel (Preview)..."
        # Run standard vercel deploy (preview)
        npx vercel
        ;;
        
    2)
        echo ""
        echo "🚀 Preparing PRODUCTION deployment..."
        
        # Ensure we are on main
        current_branch=$(git symbolic-ref --short HEAD)
        if [[ "$current_branch" != "main" ]]; then
            echo "Switching to main branch..."
            git checkout main || exit 1
        fi
        
        check_git_status

        echo "Pushing to origin/main..."
        git push origin main
        
        echo ""
        echo "Deploying to Vercel (Production)..."
        # Run vercel deploy --prod
        npx vercel --prod
        ;;
        
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment process finished."
