"""Homepage sampling and the complete-list SEO contract."""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import ROOT, build, home_article_groups, load_articles
from categories import CATEGORIES
import test_categories
from validate import validate


class HomeSelectionTests(unittest.TestCase):
    def test_latest_four_in_definition_order_with_drafts_excluded(self):
        catalog = [dict(url=f'/articles/tech-{i}.html', category='boxing-technique',
                        published=f'2026-10-{i:02}', draft=False) for i in range(1, 8)]
        catalog += [dict(url='/articles/newest-draft.html', category='combat-history',
                         published='2026-11-01', draft=True),
                    dict(url='/articles/match.html', category='match-analysis',
                         published='2026-01-01', draft=False)]
        groups = home_article_groups(list(reversed(catalog)))
        self.assertEqual([g['id'] for g in groups], ['match-analysis', 'boxing-technique'])
        self.assertEqual([a['url'] for a in groups[1]['articles']],
                         [f'/articles/tech-{i}.html' for i in [7, 6, 5, 4]])
        self.assertEqual(len(groups[0]['articles']), 1)
        self.assertEqual(groups[0]['label'], CATEGORIES['match-analysis'])
        catalog.append(dict(url='/articles/history.html', category='combat-history',
                            published='2026-11-02'))
        self.assertEqual(home_article_groups(catalog)[-1]['id'], 'combat-history')
        self.assertEqual(home_article_groups([]), [])

    def test_ties_are_deterministic_and_modified_date_does_not_reorder(self):
        items = [dict(url=f'/articles/{slug}.html', category='boxing-beginners',
                      published='2026-10-10', updated=updated)
                 for slug, updated in [('a', '2026-11-06'), ('z', '2026-10-10')]]
        self.assertEqual(home_article_groups(items), home_article_groups(items[::-1]))
        self.assertEqual(home_article_groups(items)[0]['articles'][0]['url'], '/articles/z.html')


class HomeBuildTests(unittest.TestCase):
    # Share fixture setup without inheriting/rerunning the category test methods.
    setUp = test_categories.CategoryTests.setUp

    def test_only_article_section_changes_and_samples_are_bounded(self):
        out = build(self.root)
        home = (out / 'index.html').read_text(encoding='utf-8')
        source = (ROOT / 'index.html').read_text(encoding='utf-8')
        start, end = '        <!-- Articles-->', '        <!-- Branch / CTA-->'
        self.assertEqual(source.split(start)[0], home.split(start)[0])
        self.assertEqual(source.split(end)[1], home.split(end)[1])
        manifest, legacy, articles = load_articles(self.root)
        groups = home_article_groups(legacy + articles)
        self.assertEqual(home.count('data-home-panel'), len(groups))
        self.assertEqual(home.count('data-home-panel hidden'), len(groups) - 1)
        self.assertEqual(home.count('data-article-card'), sum(len(g['articles']) for g in groups))
        self.assertLessEqual(home.count('data-article-card'), 4 * len(CATEGORIES))
        self.assertIn('href="/articles/index.html">전체 아티클 보기', home)
        self.assertIn('/js/home-articles.js', home)
        self.assertNotIn('/articles/boxing-first-class.html', home)
        self.assertEqual([a['published'] for a in legacy],
                         ['2026-05-28', '2026-05-28', '2026-05-28', '2026-06-15', '2026-05-28'])
        for group in groups:
            panel = home.split(f'id="home-panel-{group["id"]}"', 1)[1].split('</div>\n            </div>', 1)[0]
            urls = re.findall(r'<a class="article-card" href="([^"]+)"', panel)
            self.assertEqual(urls, [a['url'] for a in group['articles']])
        # Unsampled articles still have a mandatory discoverable complete-list link.
        selected = {a['url'] for g in groups for a in g['articles']}
        unsampled = next(a for a in articles if not a['draft'] and a['url'] not in selected)
        listing = out / 'articles/index.html'
        listing.write_text(listing.read_text(encoding='utf-8').replace(
            f'href="{unsampled["url"]}"', 'href="/articles/index.html"'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'missing listing link'):
            validate(self.root, out, manifest, articles)

    def test_missing_home_sample_is_rejected(self):
        out = build(self.root)
        manifest, legacy, articles = load_articles(self.root)
        sample = home_article_groups(legacy + articles)[0]['articles'][0]
        home = out / 'index.html'
        home.write_text(home.read_text(encoding='utf-8').replace(
            f'href="{sample["url"]}"', 'href="/articles/index.html"'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Homepage category selection mismatch'):
            validate(self.root, out, manifest, articles)


if __name__ == '__main__':
    unittest.main()
