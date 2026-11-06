"""Korean source data and free-form Unicode tags, without a fixed vocabulary."""
from html import escape
import re
import sys
import unicodedata
import unittest
from pathlib import Path

import yaml
import test_categories

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import build, load_articles


class TagLocalizationTests(unittest.TestCase):
    setUp = test_categories.CategoryTests.setUp

    def test_current_source_and_manifest_labels_are_korean_nfc(self):
        _, legacy, articles = load_articles(self.root)
        for article in legacy + articles:
            with self.subTest(url=article['url']):
                for value in [article['kicker'], *article['tags']]:
                    self.assertRegex(value, '[가-힣]')
                    self.assertNotRegex(value, '[A-Za-z]')
                    self.assertEqual(value, unicodedata.normalize('NFC', value))
        draft = next(a for a in articles if a['slug'] == 'boxing-first-class')
        self.assertTrue(draft['draft'])

    def test_free_form_korean_yaml_and_jinja_round_trip(self):
        _, front, body = self.draft.read_text(encoding='utf-8').split('---', 2)
        meta = yaml.safe_load(front)
        meta.update(draft=False, tags=['균형·리듬', '회복 & 휴식', '새로 제안한 태그'],
                    kicker='쉽게 배우는 균형과 리듬')
        self.draft.write_text('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)
                              + '---\n' + body, encoding='utf-8')
        out = build(self.root)
        _, _, articles = load_articles(self.root)
        article = next(a for a in articles if a['slug'] == meta['slug'])
        self.assertEqual(article['tags'], meta['tags'])
        self.assertEqual(article['kicker'], meta['kicker'])
        html = (out / 'articles/boxing-first-class.html').read_text(encoding='utf-8', errors='strict')
        for tag in meta['tags']:
            self.assertIn(f'<li>{escape(tag)}</li>', html)
        self.assertIn(f'<p class="article-kicker">{meta["kicker"]}</p>', html)
        # The source-language regression above is not an enum or a parser ban:
        # old runners and future arbitrary strings remain structurally readable.
        meta['tags'] = ['future-runner-tag']
        self.draft.write_text('---\n' + yaml.safe_dump(meta, allow_unicode=True)
                              + '---\n' + body, encoding='utf-8')
        load_articles(self.root)

    def test_korean_tag_matching_keeps_explicit_then_overlap_order(self):
        _, front, body = self.draft.read_text(encoding='utf-8').split('---', 2)
        base = yaml.safe_load(front)
        fixtures = [
            ('boxing-first-class', ['한글 시험 주제', '시험 균형'], 'boxing-beginners',
             ['/articles/stress-relief-boxing.html']),
            ('localization-test-strong', ['한글 시험 주제', '시험 균형'], 'exercise-science', []),
            ('localization-test-weak', ['한글 시험 주제'], 'boxing-beginners', []),
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
            '/articles/stress-relief-boxing.html', '/articles/localization-test-strong.html',
            '/articles/localization-test-weak.html', '/articles/index.html'])


if __name__ == '__main__':
    unittest.main()
