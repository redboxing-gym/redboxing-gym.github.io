"""Optional Chromium layout regression tests.

Run with RUN_BROWSER_TESTS=1 and Playwright Chromium installed.
Bootstrap 5.2.3 is fetched once; page resources otherwise stay local/in memory.
No source articles or image files are written.
"""
import base64
import os
import subprocess
import unittest
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get('RUN_BROWSER_TESTS') == '1',
                     'Set RUN_BROWSER_TESTS=1 for Chromium layout checks')
class ArticleImageBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import markdown
        import yaml
        from jinja2 import Environment, FileSystemLoader
        from playwright.sync_api import sync_playwright

        cls.bootstrap = urllib.request.urlopen(
            'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css',
            timeout=30).read()
        cls.original_css = subprocess.check_output(
            # Pin the pre-fix baseline so this test also works after committing.
            ['git', 'show', '23c50c7aa67883e64e2665e11f21b8af06f099ad:css/article.css'], cwd=ROOT)
        cls.current_css = (ROOT / 'css/article.css').read_bytes()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        fixture_page = cls.browser.new_page()
        cls.images = {}
        for name, size in [('wide.webp', (1600, 900)),
                           ('test-article-comic.webp', (1000, 4000)),
                           ('small.webp', (120, 80))]:
            data = fixture_page.evaluate("""([width, height]) => {
              const canvas = document.createElement('canvas');
              canvas.width = width; canvas.height = height;
              canvas.getContext('2d').fillRect(0, 0, width, height);
              return canvas.toDataURL('image/webp').split(',')[1];
            }""", list(size))
            cls.images['/assets/img/' + name] = base64.b64decode(data)
        fixture_page.close()
        source = (ROOT / 'content/articles/hangsin-boxing-gym-guide.md').read_text(
            encoding='utf-8')
        article = yaml.safe_load(source.split('---', 2)[1])
        article['body'] = markdown.markdown(
            '## Image layout\n\n![Wide](/assets/img/wide.webp)\n\n'
            '[![Comic](/assets/img/test-article-comic.webp)](/assets/img/test-article-comic.webp)'
            '\n\n![Small](/assets/img/small.webp)')
        article['url'] = '/articles/hangsin-boxing-gym-guide.html'
        env = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=True)
        html = env.get_template('article.html').render(a=article, related=[], schema={})
        card = env.get_template('article-card.html').render(a=article)
        cls.html = html.replace('<head>', '<head><base href="https://layout.test/articles/test.html">')
        cls.html = cls.html.replace('</main>',
            '<div class="container px-4 px-lg-5"><div class="row">' + card + '</div></div></main>')

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def render(self, width, original=False):
        page = self.browser.new_page(viewport={'width': width, 'height': 900})
        self.addCleanup(page.close)

        def route(request):
            url = request.request.url
            path = urlparse(url).path
            if 'bootstrap.min.css' in url:
                request.fulfill(body=self.bootstrap, content_type='text/css')
            elif path == '/css/article.css':
                request.fulfill(body=self.original_css if original else self.current_css,
                                content_type='text/css')
            elif path in self.images:
                request.fulfill(body=self.images[path], content_type='image/webp')
            elif path.startswith(('/css/', '/assets/')) and (ROOT / path.lstrip('/')).is_file():
                request.fulfill(body=(ROOT / path.lstrip('/')).read_bytes(),
                                content_type='text/css' if path.endswith('.css') else 'image/webp')
            else:
                request.fulfill(body='', content_type='text/plain')
        page.route('**/*', route)
        page.set_content(self.html, wait_until='load')
        page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
        return page

    def test_body_images_fit_without_stretching_or_overflow(self):
        baseline = self.render(360, original=True)
        self.assertGreater(baseline.evaluate('document.documentElement.scrollWidth'), 360)
        for width in [360, 390, 1024, 1440]:
            with self.subTest(viewport=width):
                page = self.render(width)
                values = page.evaluate("""() => ({
                  scroll: document.documentElement.scrollWidth,
                  body: document.querySelector('.article-body').getBoundingClientRect().width,
                  images: [...document.querySelectorAll('.article-body img')].map(i => ({
                    width: i.getBoundingClientRect().width,
                    height: i.getBoundingClientRect().height,
                    naturalWidth: i.naturalWidth, naturalHeight: i.naturalHeight
                  }))
                })""")
                self.assertLessEqual(values['scroll'], width)
                for image in values['images']:
                    self.assertLessEqual(image['width'], values['body'] + 0.1)
                    self.assertLessEqual(image['width'], image['naturalWidth'])
                    self.assertAlmostEqual(image['width'] / image['height'],
                                           image['naturalWidth'] / image['naturalHeight'], places=3)
                self.assertLessEqual(values['images'][0]['width'], 640)
                self.assertLessEqual(values['images'][1]['width'], 480)
                self.assertEqual(values['images'][2]['width'], 120)
                print('IMAGE_LAYOUT', width, values)

    def test_hero_and_card_geometry_remain_unchanged(self):
        measure = """() => ['.article-hero-image', '.article-card img'].map(s => {
          const i = document.querySelector(s), r = i.getBoundingClientRect(), c = getComputedStyle(i);
          return {width:r.width, height:r.height, fit:c.objectFit, maxHeight:c.maxHeight};
        })"""
        for width in [360, 390, 1440]:
            with self.subTest(viewport=width):
                before = self.render(width, original=True).evaluate(measure)
                after = self.render(width).evaluate(measure)
                self.assertEqual(before, after)
                print('HERO_CARD_UNCHANGED', width, after)


if __name__ == '__main__':
    unittest.main()
