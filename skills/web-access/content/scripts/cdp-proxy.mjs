#!/usr/bin/env node

/**
 * CDP Proxy - Chrome DevTools Protocol Proxy
 *
 * Provides HTTP API for Chrome CDP operations via WebSocket.
 * Connects to Chrome's remote debugging interface.
 */

import { WebSocket } from 'ws';
import http from 'http';
import url from 'url';
import path from 'path';
import fs from 'fs';

const PORT = 3456;
const CHROME_HOST = 'localhost';
const CHROME_PORT = 9222;
const IDLE_TIMEOUT = 20 * 60 * 1000; // 20 minutes

// Store active connections
const targets = new Map(); // targetId -> ws connection
let mainConnection = null;
let idleTimer = null;

// HTTP Server
const server = http.createServer(async (req, res) => {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;

    resetIdleTimer();

    try {
        if (pathname === '/health') {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ status: 'ok', targets: targets.size }));
            return;
        }

        if (pathname === '/targets') {
            const targetsList = await getTargets();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(targetsList));
            return;
        }

        if (pathname === '/new') {
            const targetUrl = parsedUrl.query.url || 'about:blank';
            const newTarget = await createNewTab(targetUrl);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(newTarget));
            return;
        }

        if (pathname === '/info') {
            const targetId = parsedUrl.query.target;
            if (!targetId) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Missing target parameter' }));
                return;
            }
            const info = await getTargetInfo(targetId);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(info));
            return;
        }

        if (pathname === '/screenshot') {
            const targetId = parsedUrl.query.target;
            const filePath = parsedUrl.query.file || '/tmp/screenshot.png';
            if (!targetId) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Missing target parameter' }));
                return;
            }
            const screenshotData = await takeScreenshot(targetId);
            fs.writeFileSync(filePath, screenshotData, 'base64');
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ file: filePath, size: screenshotData.length }));
            return;
        }

        if (pathname === '/navigate') {
            const targetId = parsedUrl.query.target;
            const navigateUrl = parsedUrl.query.url;
            if (!targetId || !navigateUrl) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Missing target or url parameter' }));
                return;
            }
            await navigateTo(targetId, navigateUrl);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true }));
            return;
        }

        if (pathname === '/back') {
            const targetId = parsedUrl.query.target;
            if (!targetId) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Missing target parameter' }));
                return;
            }
            await goBack(targetId);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true }));
            return;
        }

        if (pathname === '/scroll') {
            const targetId = parsedUrl.query.target;
            const direction = parsedUrl.query.direction;
            const y = parsedUrl.query.y;
            if (!targetId) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Missing target parameter' }));
                return;
            }
            let result;
            if (direction === 'bottom') {
                result = await scrollToBottom(targetId);
            } else if (direction === 'top') {
                result = await scrollToTop(targetId);
            } else if (y) {
                result = await scrollBy(targetId, parseInt(y));
            }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(result));
            return;
        }

        if (pathname === '/close') {
            const targetId = parsedUrl.query.target;
            if (!targetId) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Missing target parameter' }));
                return;
            }
            await closeTarget(targetId);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true }));
            return;
        }

        // POST endpoints
        if (req.method === 'POST') {
            let body = '';
            req.on('data', chunk => body += chunk);
            await new Promise(resolve => req.on('end', resolve));

            if (pathname === '/eval') {
                const targetId = parsedUrl.query.target;
                if (!targetId) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Missing target parameter' }));
                    return;
                }
                const result = await evaluate(targetId, body);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(result));
                return;
            }

            if (pathname === '/click') {
                const targetId = parsedUrl.query.target;
                if (!targetId) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Missing target parameter' }));
                    return;
                }
                const result = await jsClick(targetId, body);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(result));
                return;
            }

            if (pathname === '/clickAt') {
                const targetId = parsedUrl.query.target;
                if (!targetId) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Missing target parameter' }));
                    return;
                }
                const result = await realClick(targetId, body);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(result));
                return;
            }

            if (pathname === '/setFiles') {
                const targetId = parsedUrl.query.target;
                if (!targetId) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Missing target parameter' }));
                    return;
                }
                const result = await setFiles(targetId, body);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(result));
                return;
            }
        }

        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Not found' }));
    } catch (error) {
        console.error('Request error:', error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
    }
});

// CDP WebSocket connection management
async function connectToChrome() {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(`ws://${CHROME_HOST}:${CHROME_PORT}`);

        ws.on('open', () => {
            console.log('Connected to Chrome DevTools');
            mainConnection = ws;
            resolve(ws);
        });

        ws.on('error', (error) => {
            console.error('WebSocket error:', error);
            reject(error);
        });

        ws.on('message', (data) => {
            try {
                const message = JSON.parse(data.toString());
                handleChromeMessage(message);
            } catch (e) {
                console.error('Failed to parse message:', e);
            }
        });

        ws.on('close', () => {
            console.log('Disconnected from Chrome');
            mainConnection = null;
        });
    });
}

let messageHandlers = new Map();
let commandId = 0;

function sendCommand(method, params = {}) {
    return new Promise((resolve, reject) => {
        if (!mainConnection || mainConnection.readyState !== WebSocket.OPEN) {
            reject(new Error('Not connected to Chrome'));
            return;
        }

        const id = ++commandId;
        const message = { id, method, params };

        messageHandlers.set(id, { resolve, reject });
        mainConnection.send(JSON.stringify(message));

        // Timeout after 30 seconds
        setTimeout(() => {
            if (messageHandlers.has(id)) {
                messageHandlers.delete(id);
                reject(new Error('Command timeout'));
            }
        }, 30000);
    });
}

function handleChromeMessage(message) {
    if (message.id && messageHandlers.has(message.id)) {
        const handler = messageHandlers.get(message.id);
        messageHandlers.delete(message.id);
        if (message.error) {
            handler.reject(new Error(message.error.message || 'Command failed'));
        } else {
            handler.resolve(message.result);
        }
    }

    // Handle events
    if (message.method && message.params) {
        const targetId = message.params.targetId;
        if (targetId && targets.has(targetId)) {
            const target = targets.get(targetId);
            if (target.eventHandlers && target.eventHandlers[message.method]) {
                target.eventHandlers[message.method](message.params);
            }
        }
    }
}

async function getTargets() {
    try {
        const response = await fetch(`http://${CHROME_HOST}:${CHROME_PORT}/json/list`);
        const data = await response.json();
        return data.map(t => ({
            id: t.id,
            title: t.title,
            url: t.url,
            type: t.type
        }));
    } catch (error) {
        console.error('Failed to get targets:', error);
        return [];
    }
}

async function createNewTab(targetUrl) {
    const result = await sendCommand('Target.createTarget', { url: targetUrl });
    const targetId = result.targetId;

    // Attach to the target
    const sessionId = await sendCommand('Target.attachToTarget', { targetId, flatten: true });

    // Store the connection info
    targets.set(targetId, {
        sessionId: sessionId.sessionId,
        url: targetUrl,
        title: ''
    });

    return { targetId, sessionId: sessionId.sessionId };
}

async function getTargetInfo(targetId) {
    const target = targets.get(targetId);
    if (!target) {
        throw new Error('Target not found');
    }

    return {
        targetId,
        sessionId: target.sessionId,
        url: target.url,
        title: target.title
    };
}

async function evaluate(targetId, expression) {
    const target = targets.get(targetId);
    if (!target) {
        throw new Error('Target not found');
    }

    const result = await sendCommand('Runtime.evaluate', {
        expression,
        returnByValue: true,
        sessionId: target.sessionId
    });

    if (result.exceptionDetails) {
        return {
            error: result.result.description,
            exceptionDetails: result.exceptionDetails
        };
    }

    return {
        result: result.result.value,
        type: result.result.type
    };
}

async function jsClick(targetId, selector) {
    const script = `
        (function() {
            var el = document.querySelector('${selector}');
            if (!el) return { success: false, error: 'Element not found' };
            el.click();
            return { success: true };
        })()
    `;
    return evaluate(targetId, script);
}

async function realClick(targetId, selector) {
    const target = targets.get(targetId);
    if (!target) {
        throw new Error('Target not found');
    }

    // First get element position
    const posResult = await evaluate(targetId, `
        (function() {
            var el = document.querySelector('${selector}');
            if (!el) return { success: false, error: 'Element not found' };
            var rect = el.getBoundingClientRect();
            return {
                success: true,
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2
            };
        })()
    `);

    if (!posResult.success) {
        return posResult;
    }

    const { x, y } = posResult.result;

    // Dispatch mouse events
    await sendCommand('Input.dispatchMouseEvent', {
        type: 'mousePressed',
        x,
        y,
        button: 'left',
        clickCount: 1,
        sessionId: target.sessionId
    });

    await sendCommand('Input.dispatchMouseEvent', {
        type: 'mouseReleased',
        x,
        y,
        button: 'left',
        clickCount: 1,
        sessionId: target.sessionId
    });

    return { success: true, x, y };
}

async function setFiles(targetId, body) {
    try {
        const data = JSON.parse(body);
        const { selector, files } = data;

        const script = `
            (function() {
                var el = document.querySelector('${selector}');
                if (!el) return { success: false, error: 'Element not found' };

                // Create DataTransfer for file input
                var dataTransfer = new DataTransfer();
                var filePaths = ${JSON.stringify(files)};

                filePaths.forEach(function(filePath) {
                    // Read file and create File object
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', 'file://' + filePath, false);
                    xhr.send();

                    if (xhr.status === 200) {
                        var blob = new Blob([xhr.response], { type: 'application/octet-stream' });
                        var fileName = filePath.split('/').pop();
                        var file = new File([blob], fileName);
                        dataTransfer.items.add(file);
                    }
                });

                el.files = dataTransfer.files;
                el.dispatchEvent(new Event('change', { bubbles: true }));
                return { success: true, files: filePaths };
            })()
        `;

        return evaluate(targetId, script);
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function takeScreenshot(targetId) {
    const target = targets.get(targetId);
    if (!target) {
        throw new Error('Target not found');
    }

    const result = await sendCommand('Page.captureScreenshot', {
        format: 'png',
        sessionId: target.sessionId
    });

    return result.data;
}

async function navigateTo(targetId, navigateUrl) {
    const target = targets.get(targetId);
    if (!target) {
        throw new Error('Target not found');
    }

    await sendCommand('Page.navigate', {
        url: navigateUrl,
        sessionId: target.sessionId
    });

    target.url = navigateUrl;
    return { success: true };
}

async function goBack(targetId) {
    const target = targets.get(targetId);
    if (!target) {
        throw new Error('Target not found');
    }

    await sendCommand('Page.goBack', {
        sessionId: target.sessionId
    });

    return { success: true };
}

async function scrollToBottom(targetId) {
    const script = `
        (function() {
            window.scrollTo(0, document.body.scrollHeight);
            return { scrollY: document.body.scrollHeight };
        })()
    `;
    return evaluate(targetId, script);
}

async function scrollToTop(targetId) {
    const script = `
        (function() {
            window.scrollTo(0, 0);
            return { scrollY: 0 };
        })()
    `;
    return evaluate(targetId, script);
}

async function scrollBy(targetId, y) {
    const script = `
        (function() {
            window.scrollBy(0, ${y});
            return { scrollY: window.scrollY };
        })()
    `;
    return evaluate(targetId, script);
}

async function closeTarget(targetId) {
    if (targets.has(targetId)) {
        await sendCommand('Target.closeTarget', { targetId });
        targets.delete(targetId);
    }
    return { success: true };
}

function resetIdleTimer() {
    if (idleTimer) {
        clearTimeout(idleTimer);
    }
    idleTimer = setTimeout(() => {
        console.log('Idle timeout reached, shutting down...');
        server.close();
        process.exit(0);
    }, IDLE_TIMEOUT);
}

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Shutting down...');
    server.close();
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('Shutting down...');
    server.close();
    process.exit(0);
});

// Start server
async function main() {
    try {
        await connectToChrome();
        server.listen(PORT, () => {
            console.log(`CDP Proxy running on http://localhost:${PORT}`);
            console.log('Available endpoints:');
            console.log('  GET  /health        - Health check');
            console.log('  GET  /targets       - List all targets');
            console.log('  GET  /new?url=       - Create new tab');
            console.log('  GET  /info?target=   - Get target info');
            console.log('  POST /eval?target=  - Execute JavaScript');
            console.log('  POST /click?target= - JS click');
            console.log('  POST /clickAt?target= - Real mouse click');
            console.log('  POST /setFiles?target= - File upload');
            console.log('  GET  /screenshot?target=&file= - Take screenshot');
            console.log('  GET  /navigate?target=&url= - Navigate to URL');
            console.log('  GET  /back?target=  - Go back');
            console.log('  GET  /scroll?target=&direction=top|bottom|y= - Scroll');
            console.log('  GET  /close?target= - Close tab');
        });
        resetIdleTimer();
    } catch (error) {
        console.error('Failed to start:', error);
        process.exit(1);
    }
}

main();
