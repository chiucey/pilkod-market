# Python SDK Example
from agent_browser import AgentBrowser, BrowserError

def run_demo():
    browser = AgentBrowser(
        headless=True,
        timeout=30000
    )

    try:
        # Connect to browser
        browser.connect()
        print("Browser connected")

        # Navigate to page
        page = browser.navigate('https://example.com')
        print(f"Navigated to: {page.url}")

        # Take screenshot
        browser.screenshot(path='./example.png')
        print("Screenshot saved")

        # Extract data
        links = browser.extract('a', {
            'text': '::text',
            'href': '@href'
        })
        print(f"Found {len(links)} links")

        # Perform actions
        browser.click('#some-button')
        browser.type('#search-input', 'search query')

        # Wait for result
        browser.wait_for_selector('.results', state='visible')

        # Evaluate custom JavaScript
        title = browser.evaluate('() => document.title')
        print(f"Page title: {title}")

    except BrowserError as e:
        print(f"Browser error: {e}")
    finally:
        browser.close()

# Batch operations example
def batch_example():
    browser = AgentBrowser()
    browser.connect()

    commands = [
        {'cmd': 'navigate', 'target': 'https://site1.com'},
        {'cmd': 'screenshot', 'path': './site1.png'},
        {'cmd': 'navigate', 'target': 'https://site2.com'},
        {'cmd': 'screenshot', 'path': './site2.png'}
    ]

    results = browser.batch(commands)
    print(f"Batch results: {results}")

    browser.close()

# Context manager example
def context_manager_example():
    with AgentBrowser() as browser:
        browser.navigate('https://example.com')
        browser.screenshot(path='./example.png')

# Event handling example
def events_example():
    browser = AgentBrowser()

    def on_console(msg):
        print(f"Console [{msg['type']}]: {msg['text']}")

    def on_error(err):
        print(f"Page error: {err}")

    browser.on('console', on_console)
    browser.on('error', on_error)

    browser.connect()
    browser.navigate('https://example.com')
    browser.close()

if __name__ == '__main__':
    run_demo()
