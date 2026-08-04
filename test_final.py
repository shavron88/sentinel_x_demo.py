import urllib.request, time

time.sleep(2)

# Check dashboard page
resp = urllib.request.urlopen('http://127.0.0.1:5000/')
html = resp.read().decode()

# Check CSS for overflow settings
css_resp = urllib.request.urlopen('http://127.0.0.1:5000/static/css/style.css')
css_content = css_resp.read().decode()

print("=== CSS Checks ===")
print("body overflow-y:auto:", "overflow-y:auto" in css_content)
print("body overflow:hidden:", "overflow:hidden" in css_content)
print("container min-height:", "min-height:100vh" in css_content and ".container" in css_content)

# Check HTML
print("\n=== HTML Content Checks ===")
for section in ['dashboard-header', 'stats-grid', 'stat-card', 'dashboard-grid', 
                'bottom-grid', 'performance-grid', 'dashboard-footer',
                'live-camera', 'timeline', 'gallery', 'ai-summary',
                'security-map', 'threat-level', 'person-count']:
    print(f"  {section}: {'FOUND' if section in html else 'MISSING'}")

# Check sidebar
print("\n=== Sidebar Links ===")
for link in ['/', '/cameras', '/incidents', '/evidence', '/analytics', '/reports', '/settings']:
    print(f"  href={link}: {'FOUND' if ('href=\"' + link + '\"') in html else 'MISSING'}")

# Check all routes
print("\n=== Route Tests ===")
routes = ['/', '/cameras', '/incidents', '/evidence', '/analytics', '/reports', '/settings']
for path in routes:
    try:
        r = urllib.request.urlopen(f'http://127.0.0.1:5000{path}', timeout=5)
        has_content = len(r.read()) > 1000
        print(f"  {path:15s}: {r.status} - {'OK' if has_content else 'EMPTY'}")
    except Exception as e:
        print(f"  {path:15s}: FAILED - {e}")
