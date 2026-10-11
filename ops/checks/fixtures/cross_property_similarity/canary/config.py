# Canary config: same shape as GCI _similarity_check.py (literal assignments only).
THRESHOLD = 0.30
SHINGLE_N = 5
PAIRS = [
    ('index.html', 'index.html', 'homepage vs homepage (planted copy)'),
]
STRIP_PATTERNS = [
    r'<header class="site-nav".*?</header>',
    r'<footer.*?</footer>',
    r'<script.*?</script>',
    r'<style.*?</style>',
]
