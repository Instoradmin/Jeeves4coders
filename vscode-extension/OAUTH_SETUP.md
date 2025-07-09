# Jeeves4coders OAuth2 Setup Guide

This guide will help you set up Google OAuth2 authentication for Jeeves4coders VS Code extension.

## Prerequisites

- Google Cloud Platform account
- VS Code with Jeeves4coders extension installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

## Step 2: Enable APIs

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Enable the following APIs:
   - Google+ API (for user profile information)
   - OAuth2 API

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type (unless you're using Google Workspace)
3. Fill in the required information:
   - **App name**: Jeeves4coders
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. Add scopes:
   - `openid`
   - `email`
   - `profile`
5. Add test users (your email and any other users who will use the extension)

## Step 4: Create OAuth2 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Choose **Desktop application** as the application type
4. Name it "Jeeves4coders VS Code Extension"
5. Add authorized redirect URIs:
   - `http://localhost:8080/oauth/callback`
6. Download the JSON file or copy the Client ID

## Step 5: Configure Jeeves4coders

1. Open VS Code
2. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
3. Run "Jeeves4coders: Configure Accounts"
4. In the SSO section, enter your Google OAuth2 Client ID
5. Click "Connect with Google"
6. Complete the authentication in your browser

## Step 6: Connect Additional Services

### GitHub
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with appropriate scopes:
   - `repo` (for repository access)
   - `user` (for user information)
   - `workflow` (for GitHub Actions)
3. Copy the token and enter it in Jeeves4coders configuration

### JIRA
1. Go to your JIRA instance
2. Go to Account Settings > Security > API tokens
3. Create a new API token
4. Use your email and the API token in Jeeves4coders configuration

### Confluence
1. Use the same API token from JIRA (if using Atlassian Cloud)
2. Or create a separate API token following the same process
3. Enter your Confluence base URL and credentials

## Security Best Practices

1. **Keep your Client ID secure**: Don't share it publicly
2. **Use environment variables**: Store sensitive information securely
3. **Regular token rotation**: Refresh tokens periodically
4. **Minimal scopes**: Only request necessary permissions
5. **Monitor usage**: Check Google Cloud Console for API usage

## Troubleshooting

### Common Issues

1. **"Invalid Client ID"**
   - Verify the Client ID is correct
   - Ensure the OAuth consent screen is configured
   - Check that the redirect URI is exactly `http://localhost:8080/oauth/callback`

2. **"Access Denied"**
   - Make sure your email is added as a test user
   - Verify the OAuth consent screen is published or in testing mode

3. **"Connection Timeout"**
   - Check your firewall settings
   - Ensure port 8080 is available
   - Try disabling antivirus temporarily

4. **"Token Expired"**
   - The extension will automatically refresh tokens
   - If issues persist, disconnect and reconnect

### Getting Help

1. Check the VS Code Developer Console for error messages
2. Review the extension logs in VS Code Output panel
3. Create an issue on the [GitHub repository](https://github.com/Instoradmin/Jeeves4coders/issues)

## Advanced Configuration

### Custom OAuth2 Provider

If you want to use a different OAuth2 provider:

1. Modify the `configManager.ts` file
2. Update the OAuth2 endpoints
3. Adjust the scope and user info endpoints
4. Test thoroughly with your provider

### Enterprise Setup

For enterprise environments:

1. Use Google Workspace with internal app configuration
2. Set up domain-wide delegation if needed
3. Configure appropriate organizational policies
4. Consider using service accounts for automated workflows

## API Limits and Quotas

- Google OAuth2 API has generous limits for authentication
- Monitor your usage in Google Cloud Console
- Consider implementing caching for user information
- Be mindful of rate limits when making API calls

## Privacy and Data Handling

Jeeves4coders:
- Only requests necessary user information (email, name, profile picture)
- Stores tokens securely using VS Code's secret storage
- Does not share user data with third parties
- Allows users to disconnect and clear all data at any time

## Updates and Maintenance

- Keep the extension updated for security patches
- Monitor Google Cloud Console for any API changes
- Review and update scopes as needed
- Regularly check token expiration and refresh mechanisms
