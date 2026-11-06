"""Opt-in Chromium checks against the actual generated static site.

RUN_BROWSER_TESTS=1 requires Playwright and Chromium. QA_OUTPUT_DIR optionally
keeps viewport screenshots outside the repository for human review.
"""
import functools
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import ROOT, build
from categories import CATEGORIES


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@unittest.skipUnless(os.environ.get('RUN_BROWSER_TESTS') == '1',
                     'Set RUN_BROWSER_TESTS=1 for Chromium category checks')
class CategoryFilterBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        for name in ['assets', 'css', 'js', 'articles', 'content', 'templates']:
            shutil.copytree(ROOT / name, cls.root / name)
        for name in ['index.html', 'robots.txt', 'sitemap.xml', 'sitemap-pages.xml',
                     'google23bb310db4f0bb3a.html', 'navera7eccb22797895e11709710faa396cbf.html']:
            shutil.copy2(ROOT / name, cls.root / name)
        out = build(cls.root)
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0),
            functools.partial(QuietHandler, directory=str(out)))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.addClassCleanup(cls.server.server_close)
        cls.addClassCleanup(cls.server.shutdown)
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.bootstrap = urllib.request.urlopen(
            'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css', timeout=30).read()
        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)
        cls.browser = cls.playwright.chromium.launch()
        cls.addClassCleanup(cls.browser.close)

    def page(self, width=1440, javascript=True):
        context = self.browser.new_context(viewport={'width': width, 'height': 1000},
                                           java_script_enabled=javascript)
        self.addCleanup(context.close)
        context.route('https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css',
                      lambda route: route.fulfill(body=self.bootstrap, content_type='text/css'))
        return context.new_page()

    def screenshot(self, page, name):
        directory = os.environ.get('QA_OUTPUT_DIR')
        if directory:
            target = Path(directory)
            target.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(target / f'{name}.png'))

    def test_all_filters_keyboard_selection_and_no_navigation(self):
        page = self.page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(self.url + '/articles/index.html', wait_until='networkidle')
        start_url = page.url
        navigations = []
        page.on('framenavigated', lambda frame: navigations.append(frame.url))
        cards = page.locator('[data-article-card]')
        total = cards.count()
        self.assertGreater(total, 5)
        self.assertEqual(page.locator('[data-article-card]:visible').count(), total)
        buttons = page.locator('[data-category-filter] button')
        self.assertEqual(buttons.count(), 8)
        for category in CATEGORIES:
            button = page.locator(f'button[data-category="{category}"]')
            button.click()
            visible = page.locator('[data-article-card]:visible')
            self.assertEqual(visible.count(), page.locator(
                f'[data-article-card][data-category="{category}"]').count())
            self.assertTrue(all(value == category for value in visible.evaluate_all(
                '(cards) => cards.map(card => card.dataset.category)')))
            self.assertEqual(page.locator('button[aria-pressed="true"]').count(), 1)
            self.assertEqual(button.get_attribute('aria-pressed'), 'true')
            self.assertIn(str(visible.count()) + '개 글', page.get_by_role('status').inner_text())
            self.assertEqual(page.locator('[data-category-empty]').is_visible(), visible.count() == 0)
        first = page.get_by_role('button', name='전체 보기', exact=True)
        first.focus()
        page.keyboard.press('Space')
        self.assertEqual(page.locator('[data-article-card]:visible').count(), total)
        page.keyboard.press('Tab')
        self.assertEqual(page.locator(':focus').get_attribute('data-category'), 'match-analysis')
        page.keyboard.press('Enter')
        self.assertEqual(page.locator(':focus').get_attribute('aria-pressed'), 'true')
        self.assertEqual(page.url, start_url)
        self.assertEqual(navigations, [])
        self.assertEqual(errors, [])

    def test_without_javascript_all_links_and_cards_remain_visible(self):
        page = self.page(width=390, javascript=False)
        page.goto(self.url + '/articles/index.html', wait_until='networkidle')
        self.assertFalse(page.locator('[data-category-filter]').is_visible())
        cards = page.locator('[data-article-card]')
        self.assertEqual(page.locator('[data-article-card]:visible').count(), cards.count())
        self.assertEqual(cards.locator('a.article-card[href]').count(), cards.count())
        self.assertGreater(cards.count(), 5)
        self.screenshot(page, 'list-no-javascript-390')

    def test_desktop_mobile_list_home_and_article_layout(self):
        measurements = []
        for width in [360, 390, 1440]:
            page = self.page(width=width)
            for path, name in [('/articles/index.html', 'list'),
                               ('/articles/boxing-breathing-basics.html', 'article'),
                               ('/#articles', 'home')]:
                with self.subTest(width=width, page=name):
                    page.goto(self.url + path, wait_until='networkidle')
                    values = page.evaluate('''() => ({
                        viewport: innerWidth, scroll: document.documentElement.scrollWidth,
                        brokenImages: [...document.images].filter(i => i.complete && !i.naturalWidth).length
                    })''')
                    self.assertLessEqual(values['scroll'], width)
                    self.assertEqual(values['brokenImages'], 0)
                    if name == 'list':
                        self.assertTrue(page.locator('[data-category-filter]').is_visible())
                        self.assertEqual(page.locator('[data-category-filter] button').count(), 8)
                        page.get_by_role('button', name='운동과학', exact=True).click()
                    elif name == 'article':
                        self.assertTrue(page.locator('.article-taxonomy .article-category').is_visible())
                        self.assertGreater(page.locator('.article-tags li').count(), 0)
                    else:
                        self.assertEqual(page.locator('#articles .article-category').count(),
                                         page.locator('#articles .article-card').count())
                    measurements.append(dict(page=name, **values))
                    self.screenshot(page, f'{name}-{width}')
        print('CATEGORY_LAYOUT', json.dumps(measurements))


if __name__ == '__main__':
    unittest.main()
