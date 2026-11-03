// Node.js SDK Example
const { AgentBrowser } = require('agent-browser-sdk');

async function runDemo() {
  const browser = new AgentBrowser({
    headless: true,
    timeout: 30000
  });

  try {
    // Connect to browser
    await browser.connect();
    console.log('Browser connected');

    // Navigate to page
    const page = await browser.navigate('https://example.com');
    console.log(`Navigated to: ${page.url}`);

    // Take screenshot
    await browser.screenshot({ path: './example.png' });

    // Extract data
    const links = await browser.extract('a', {
      text: '::text',
      href: '@href'
    });
    console.log(`Found ${links.length} links`);

    // Perform actions
    await browser.click('#some-button');
    await browser.type('#search-input', 'search query');

    // Wait for result
    await browser.waitForSelector('.results', { state: 'visible' });

    // Evaluate custom JavaScript
    const title = await browser.evaluate(() => document.title);

    console.log(`Page title: ${title}`);

  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
}

// Batch operations example
async function batchExample() {
  const browser = new AgentBrowser();
  await browser.connect();

  const commands = [
    { cmd: 'navigate', target: 'https://site1.com' },
    { cmd: 'screenshot', path: './site1.png' },
    { cmd: 'navigate', target: 'https://site2.com' },
    { cmd: 'screenshot', path: './site2.png' }
  ];

  const results = await browser.batch(commands);
  console.log('Batch results:', results);

  await browser.close();
}

// Event handling example
async function eventsExample() {
  const browser = new AgentBrowser();

  browser.on('console', (msg) => {
    console.log(`Console [${msg.type}]: ${msg.text}`);
  });

  browser.on('error', (err) => {
    console.error('Page error:', err);
  });

  browser.on('request', (req) => {
    if (req.url.includes('api/')) {
      console.log('API request:', req.url);
    }
  });

  await browser.connect();
  await browser.navigate('https://example.com');
  await browser.close();
}

runDemo();
