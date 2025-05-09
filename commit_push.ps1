# commit_push.ps1
# Commits all changes in the repository and pushes to GitHub

# Set repository directory
\ = "C:\Users\korit\OneDrive\Desktop\library-management-system"

# Navigate to repository
Set-Location -Path \

# Check for changes
\ = git status --porcelain
if (-not \) {
    Write-Host "No changes to commit."
    exit 0
}

# Stage all changes
git add .

# Commit changes
\ = "Update test_app.py to fix test_create_login_screen button count"
git commit -m \

# Push to remote repository
\ = "main"
git push origin \

Write-Host "Changes committed and pushed to GitHub. Check GitHub Actions for results."
