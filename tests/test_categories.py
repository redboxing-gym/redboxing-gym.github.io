"""Category migration, output and existing recommendation contract regressions."""
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import ROOT, build, load_articles
from categories import CATEGORIES


class CategoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['assets', 'css', 'js', 'articles', 'content', 'templates']:
            shutil.copytree(ROOT / name, self.root / name)
        for path in ROOT.glob('*.html'):
            shutil.copy2(path, self.root / path.name)
        for name in ['robots.txt', 'sitemap.xml', 'sitemap-pages.xml']:
            shutil.copy2(ROOT / name, self.root / name)
        self.draft = self.root / 'content/articles/boxing-first-class.md'

    def test_markdown_category_required_and_validated_for_drafts_and_public(self):
        source = self.draft.read_text(encoding='utf-8')
        for draft in [True, False]:
            for value in [None, '', 'unknown', 'Boxing-Technique', [], {}, True, 42]:
                with self.subTest(draft=draft, value=value):
                    _, front, body = source.split('---', 2)
                    meta = yaml.safe_load(front)
                    meta['draft'] = draft
                    if value is None:
                        del meta['category']
                    else:
                        meta['category'] = value
                    self.draft.write_text('---\n' + yaml.safe_dump(meta, allow_unicode=True)
                                          + '---\n' + body, encoding='utf-8')
                    with self.assertRaisesRegex(ValueError, '(missing|invalid) category'):
                        load_articles(self.root)

    def test_legacy_category_required_and_validated(self):
        path = self.root / 'content/legacy-articles.json'
        source = path.read_text(encoding='utf-8')
        for value in [None, 'unknown', [], True]:
            with self.subTest(value=value):
                manifest = json.loads(source)
                if value is None:
                    del manifest['articles'][0]['category']
                else:
                    manifest['articles'][0]['category'] = value
                path.write_text(json.dumps(manifest), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, '(missing|invalid) category'):
                    load_articles(self.root)

    def test_every_category_is_accepted(self):
        source = self.draft.read_text(encoding='utf-8')
        for category, label in CATEGORIES.items():
            with self.subTest(category=category):
                self.draft.write_text(source.replace('category: "boxing-beginners"',
                                                      f'category: "{category}"'), encoding='utf-8')
                _, _, articles = load_articles(self.root)
                article = next(a for a in articles if a['slug'] == 'boxing-first-class')
                self.assertEqual(article['category_label'], label)

    def test_cards_filters_details_and_protected_output(self):
        out = build(self.root)
        manifest, legacy, articles = load_articles(self.root)
        public = [a for a in articles if not a['draft']]
        home = (out / 'index.html').read_text(encoding='utf-8')
        listing = (out / 'articles/index.html').read_text(encoding='utf-8')
        self.assertEqual(listing.count('data-article-card'), len(legacy) + len(public))
        self.assertEqual(home.count('class="article-category"'), len(legacy) + len(public))
        self.assertEqual(re.findall(r'<button[^>]+data-category="([^"]+)"', listing),
                         ['all', *CATEGORIES])
        self.assertIn('data-category-filter hidden', listing)
        self.assertIn('aria-pressed="true"', listing)
        self.assertNotRegex(listing, r'<div[^>]+data-article-card[^>]*\bhidden\b')
        self.assertNotIn('/articles/boxing-first-class.html', listing)
        self.assertFalse((out / 'articles/boxing-first-class.html').exists())
        for article in legacy + public:
            self.assertIn(f'href="{article["url"]}"', listing)
            self.assertIn(article['category_label'], listing)
        for article in public:
            html = (out / article['url'].lstrip('/')).read_text(encoding='utf-8')
            self.assertIn(f'카테고리 · {article["category_label"]}', html)
            self.assertIn('href="/articles/index.html">전체 글 목록 보기', html)
            for tag in article['tags']:
                self.assertIn(f'<li>{tag}</li>', html)
        for path in manifest['protected']:
            self.assertEqual((self.root / path).read_bytes(), (out / path).read_bytes())
        self.assertEqual((ROOT / 'index.html').read_bytes(), (self.root / 'index.html').read_bytes())

    def test_explicit_related_then_tag_overlap_without_category_scoring(self):
        source = self.draft.read_text(encoding='utf-8')
        _, front, body = source.split('---', 2)
        base = yaml.safe_load(front)
        fixtures = [
            ('boxing-first-class', ['signal-a', 'signal-b'], 'boxing-beginners',
             ['/articles/stress-relief-boxing.html']),
            ('category-test-strong', ['signal-a', 'signal-b'], 'exercise-science', []),
            ('category-test-weak', ['signal-a'], 'boxing-beginners', []),
        ]
        for slug, tags, category, related in fixtures:
            meta = dict(base, slug=slug, tags=tags, category=category, related=related, draft=False,
                        canonical=f'https://redboxing-gym.github.io/articles/{slug}.html')
            (self.draft.parent / f'{slug}.md').write_text(
                '---\n' + yaml.safe_dump(meta, allow_unicode=True) + '---\n' + body, encoding='utf-8')
        out = build(self.root)
        html = (out / 'articles/boxing-first-class.html').read_text(encoding='utf-8')
        panel = re.search(r'<div class="article-related-panel">(.*?)</div>', html, re.S)[1]
        self.assertEqual(re.findall(r'href="([^"]+)"', panel), [
            '/articles/stress-relief-boxing.html', '/articles/category-test-strong.html',
            '/articles/category-test-weak.html', '/articles/index.html'])


if __name__ == '__main__':
    unittest.main()
