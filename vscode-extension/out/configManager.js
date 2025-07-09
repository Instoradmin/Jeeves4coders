"use strict";
/**
 * Jeeves4coders Configuration Manager
 * Handles account connections, SSO authentication, and configuration management
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConfigurationManager = void 0;
const vscode = require("vscode");
const crypto = require("crypto");
const axios_1 = require("axios");
class ConfigurationManager {
    constructor(context) {
        this.context = context;
        this.secretStorage = context.secrets;
    }
    /**
     * Get current SSO configuration
     */
    async getSSOConfig() {
        const config = vscode.workspace.getConfiguration('jeeves4coders');
        const accessToken = await this.secretStorage.get('sso.accessToken');
        const refreshToken = await this.secretStorage.get('sso.refreshToken');
        const userInfoStr = await this.secretStorage.get('sso.userInfo');
        return {
            enabled: config.get('ssoEnabled', true),
            clientId: config.get('oauth.clientId', ''),
            accessToken,
            refreshToken,
            expiresAt: await this.getStoredValue('sso.expiresAt'),
            userInfo: userInfoStr ? JSON.parse(userInfoStr) : undefined
        };
    }
    /**
     * Initiate Google OAuth2 SSO flow
     */
    async initiateSSO() {
        try {
            const config = await this.getSSOConfig();
            if (!config.clientId) {
                const clientId = await vscode.window.showInputBox({
                    prompt: 'Enter your Google OAuth2 Client ID',
                    placeHolder: 'your-client-id.googleusercontent.com',
                    ignoreFocusOut: true
                });
                if (!clientId) {
                    return false;
                }
                await vscode.workspace.getConfiguration('jeeves4coders').update('oauth.clientId', clientId, vscode.ConfigurationTarget.Global);
                config.clientId = clientId;
            }
            // Generate state for security
            const state = crypto.randomBytes(32).toString('hex');
            await this.secretStorage.store('oauth.state', state);
            // Create OAuth2 URL
            const redirectUri = 'http://localhost:8080/oauth/callback';
            const scope = 'openid email profile';
            const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
                `client_id=${encodeURIComponent(config.clientId)}&` +
                `redirect_uri=${encodeURIComponent(redirectUri)}&` +
                `response_type=code&` +
                `scope=${encodeURIComponent(scope)}&` +
                `state=${encodeURIComponent(state)}`;
            // Start local server to handle callback
            const success = await this.startOAuthServer(state);
            if (success) {
                // Open browser for authentication
                vscode.env.openExternal(vscode.Uri.parse(authUrl));
                vscode.window.showInformationMessage('Please complete the authentication in your browser. The callback server is running on localhost:8080.');
                return true;
            }
            return false;
        }
        catch (error) {
            vscode.window.showErrorMessage(`SSO authentication failed: ${error}`);
            return false;
        }
    }
    /**
     * Start local OAuth callback server
     */
    async startOAuthServer(expectedState) {
        return new Promise((resolve) => {
            const http = require('http');
            const server = http.createServer(async (req, res) => {
                const url = new URL(req.url, 'http://localhost:8080');
                if (url.pathname === '/oauth/callback') {
                    const code = url.searchParams.get('code');
                    const state = url.searchParams.get('state');
                    const error = url.searchParams.get('error');
                    if (error) {
                        res.writeHead(400, { 'Content-Type': 'text/html' });
                        res.end(`<h1>Authentication Failed</h1><p>Error: ${error}</p>`);
                        server.close();
                        resolve(false);
                        return;
                    }
                    if (state !== expectedState) {
                        res.writeHead(400, { 'Content-Type': 'text/html' });
                        res.end('<h1>Authentication Failed</h1><p>Invalid state parameter</p>');
                        server.close();
                        resolve(false);
                        return;
                    }
                    if (code) {
                        try {
                            const success = await this.exchangeCodeForTokens(code);
                            if (success) {
                                res.writeHead(200, { 'Content-Type': 'text/html' });
                                res.end(`
                                    <h1>Authentication Successful!</h1>
                                    <p>You can now close this window and return to VS Code.</p>
                                    <script>window.close();</script>
                                `);
                                vscode.window.showInformationMessage('SSO authentication successful!');
                            }
                            else {
                                res.writeHead(400, { 'Content-Type': 'text/html' });
                                res.end('<h1>Authentication Failed</h1><p>Failed to exchange code for tokens</p>');
                            }
                        }
                        catch (error) {
                            res.writeHead(500, { 'Content-Type': 'text/html' });
                            res.end(`<h1>Authentication Failed</h1><p>Error: ${error}</p>`);
                        }
                        server.close();
                        resolve(true);
                    }
                }
            });
            server.listen(8080, () => {
                console.log('OAuth callback server started on port 8080');
            });
            // Timeout after 5 minutes
            setTimeout(() => {
                server.close();
                resolve(false);
            }, 300000);
        });
    }
    /**
     * Exchange authorization code for access tokens
     */
    async exchangeCodeForTokens(code) {
        try {
            const config = await this.getSSOConfig();
            const redirectUri = 'http://localhost:8080/oauth/callback';
            const response = await axios_1.default.post('https://oauth2.googleapis.com/token', {
                client_id: config.clientId,
                code: code,
                grant_type: 'authorization_code',
                redirect_uri: redirectUri
            });
            const { access_token, refresh_token, expires_in } = response.data;
            // Store tokens securely
            await this.secretStorage.store('sso.accessToken', access_token);
            if (refresh_token) {
                await this.secretStorage.store('sso.refreshToken', refresh_token);
            }
            const expiresAt = Date.now() + (expires_in * 1000);
            await this.storeValue('sso.expiresAt', expiresAt);
            // Get user info
            const userInfo = await this.getUserInfo(access_token);
            if (userInfo) {
                await this.secretStorage.store('sso.userInfo', JSON.stringify(userInfo));
            }
            return true;
        }
        catch (error) {
            console.error('Token exchange failed:', error);
            return false;
        }
    }
    /**
     * Get user information from Google API
     */
    async getUserInfo(accessToken) {
        try {
            const response = await axios_1.default.get('https://www.googleapis.com/oauth2/v2/userinfo', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            return response.data;
        }
        catch (error) {
            console.error('Failed to get user info:', error);
            return null;
        }
    }
    /**
     * Check if SSO token is valid and refresh if needed
     */
    async validateAndRefreshSSO() {
        try {
            const config = await this.getSSOConfig();
            if (!config.accessToken) {
                return false;
            }
            // Check if token is expired
            if (config.expiresAt && Date.now() >= config.expiresAt) {
                return await this.refreshSSO();
            }
            return true;
        }
        catch (error) {
            console.error('SSO validation failed:', error);
            return false;
        }
    }
    /**
     * Refresh SSO tokens
     */
    async refreshSSO() {
        try {
            const config = await this.getSSOConfig();
            if (!config.refreshToken) {
                return false;
            }
            const response = await axios_1.default.post('https://oauth2.googleapis.com/token', {
                client_id: config.clientId,
                refresh_token: config.refreshToken,
                grant_type: 'refresh_token'
            });
            const { access_token, expires_in } = response.data;
            await this.secretStorage.store('sso.accessToken', access_token);
            const expiresAt = Date.now() + (expires_in * 1000);
            await this.storeValue('sso.expiresAt', expiresAt);
            return true;
        }
        catch (error) {
            console.error('SSO refresh failed:', error);
            return false;
        }
    }
    /**
     * Get account configuration
     */
    async getAccountConfig(type) {
        const config = vscode.workspace.getConfiguration('jeeves4coders');
        const token = await this.secretStorage.get(`${type}.token`);
        const userInfoStr = await this.secretStorage.get(`${type}.userInfo`);
        return {
            type,
            connected: config.get(`${type}.connected`, false),
            token,
            username: userInfoStr ? JSON.parse(userInfoStr).username : undefined,
            email: userInfoStr ? JSON.parse(userInfoStr).email : undefined,
            baseUrl: await this.getStoredValue(`${type}.baseUrl`),
            lastConnected: await this.getStoredValue(`${type}.lastConnected`)
        };
    }
    /**
     * Store account configuration
     */
    async storeAccountConfig(config) {
        const vsConfig = vscode.workspace.getConfiguration('jeeves4coders');
        // Update connection status
        await vsConfig.update(`${config.type}.connected`, config.connected, vscode.ConfigurationTarget.Global);
        // Store sensitive data in secret storage
        if (config.token) {
            await this.secretStorage.store(`${config.type}.token`, config.token);
        }
        if (config.username || config.email) {
            await this.secretStorage.store(`${config.type}.userInfo`, JSON.stringify({
                username: config.username,
                email: config.email
            }));
        }
        if (config.baseUrl) {
            await this.storeValue(`${config.type}.baseUrl`, config.baseUrl);
        }
        await this.storeValue(`${config.type}.lastConnected`, new Date().toISOString());
    }
    /**
     * Clear account configuration
     */
    async clearAccountConfig(type) {
        const config = vscode.workspace.getConfiguration('jeeves4coders');
        await config.update(`${type}.connected`, false, vscode.ConfigurationTarget.Global);
        await this.secretStorage.delete(`${type}.token`);
        await this.secretStorage.delete(`${type}.userInfo`);
        await this.context.globalState.update(`${type}.baseUrl`, undefined);
        await this.context.globalState.update(`${type}.lastConnected`, undefined);
    }
    /**
     * Clear all SSO data
     */
    async clearSSO() {
        await this.secretStorage.delete('sso.accessToken');
        await this.secretStorage.delete('sso.refreshToken');
        await this.secretStorage.delete('sso.userInfo');
        await this.secretStorage.delete('oauth.state');
        await this.context.globalState.update('sso.expiresAt', undefined);
    }
    /**
     * Helper method to store non-sensitive values
     */
    async storeValue(key, value) {
        await this.context.globalState.update(key, value);
    }
    /**
     * Helper method to get stored non-sensitive values
     */
    async getStoredValue(key) {
        return this.context.globalState.get(key);
    }
}
exports.ConfigurationManager = ConfigurationManager;
//# sourceMappingURL=configManager.js.map