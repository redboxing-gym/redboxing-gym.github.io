"""Recommendation ranking policy and actual full-build integration."""
import hashlib
from itertools import permutations
import re
import sys
import unittest
from pathlib import Path

import yaml
import test_categories

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import build, load_articles
from recommendations import RELATED_CATEGORIES, recommend_related, relevance_score, topic_tokens


def article(slug, **values):
    return dict(url=f'/articles/{slug}.html', category=values.pop('category', 'boxing-technique'),
                published=values.pop('published', '2026-10-01'), title=values.pop('title', ''),
                tags=values.pop('tags', []), keywords=values.pop('keywords', []), **values)


def urls(items):
    return [item['url'] for item in items]


class RecommendationTests(unittest.TestCase):
    def test_specific_tags_and_keywords_precede_category_and_general_words(self):
        source = article('source', tags=['잽', '복싱'], keywords=['거리 조절'])
        tag = article('tag', tags=['잽'], category='match-analysis', published='2020-01-01')
        keyword = article('keyword', keywords=['거리 조절'], category='exercise-science')
        general = article('general', tags=['복싱', '초보자'], keywords=['초보 복싱'],
                          title='복싱 운동 입문 가이드', published='2026-11-10')
        self.assertEqual(relevance_score(source, tag), 24)
        self.assertEqual(relevance_score(source, keyword), 20)
        self.assertEqual(relevance_score(source, general), 0)
        self.assertEqual(urls(recommend_related(source, [general, keyword, tag])),
                         urls([tag, keyword, general]))

    def test_keyword_tag_cross_match_and_metadata_phrases(self):
        source = article('source', tags=['거리 조절'], keywords=['잽'])
        cross = article('cross', keywords=['거리 조절'])
        title = article('title', title='잽을 뻗는 타이밍', category='combat-history')
        description = article('description', description='거리 조절을 익힙니다.',
                              category='combat-culture')
        self.assertEqual(relevance_score(source, cross), 16)
        self.assertEqual(relevance_score(source, title), 8)
        self.assertEqual(relevance_score(source, description), 4)
        self.assertEqual(relevance_score(source, article('substring', title='잽싸게 움직이기')), 0)
        self.assertEqual(urls(recommend_related(source, [description, title, cross])),
                         urls([cross, title, description]))

    def test_title_and_metadata_cross_match_is_symmetric(self):
        left = article('left', title='리듬 균형')
        right = article('right', title='균형 리듬', category='match-analysis')
        same_category = article('same-category', published='2026-11-10')
        self.assertEqual(relevance_score(left, right), 4)
        self.assertEqual(urls(recommend_related(left, [same_category, right]))[0], right['url'])
        metadata = article('metadata', title='리듬', description='균형')
        self.assertEqual(relevance_score(left, metadata), 3)
        self.assertEqual(relevance_score(left, metadata), relevance_score(metadata, left))

    def test_normalization_repetition_and_evidence_caps(self):
        self.assertEqual(topic_tokens('복싱 초보자 운동 방법 123 ＪＡＢ 잽을'), ('jab', '잽'))
        source = article('source', tags=['균형', '리듬', '회복', '지구력'])
        repeated = article('repeated', tags=source['tags'] * 5)
        self.assertEqual(relevance_score(source, repeated), 72)
        self.assertEqual(relevance_score(article('a', tags=['café']),
                                        article('b', tags=['cafe\u0301'])), 24)

    def test_same_category_stage_precedes_associated_and_global(self):
        source = article('source', title='리듬')
        direct = article('direct', title='리듬', tags=['리듬'], category='combat-culture')
        same = article('same', published='2020-01-01')
        associated = article('associated', title='리듬', category='boxing-beginners')
        global_item = article('global', title='리듬', category='exercise-science')
        self.assertEqual(urls(recommend_related(source, [global_item, associated, same, direct])),
                         urls([direct, same, associated]))

    def test_all_associated_category_pools_and_score_before_table_order(self):
        expected = {
            'boxing-technique': ('boxing-beginners', 'workout-programs'),
            'boxing-beginners': ('boxing-technique', 'workout-programs'),
            'exercise-science': ('workout-programs', 'weight-management', 'boxing-technique'),
            'workout-programs': ('exercise-science', 'weight-management', 'boxing-beginners'),
            'weight-management': ('exercise-science', 'workout-programs'),
            'match-analysis': ('boxing-technique', 'combat-history'),
            'combat-culture': ('combat-history', 'match-analysis'),
            'combat-history': ('match-analysis', 'combat-culture'),
        }
        self.assertEqual(RELATED_CATEGORIES, expected)
        for category, related in expected.items():
            with self.subTest(category=category):
                source = article('source', category=category, title='리듬')
                candidates = [article(f'candidate-{i}', category=value,
                                      title='리듬' if i == 1 else '',
                                      published='2020-01-01' if i == 1 else '2026-11-10')
                              for i, value in enumerate(related)]
                global_item = article('global', category='other', title='리듬')
                expected_order = [candidates[1], candidates[0], *candidates[2:], global_item][:3]
                self.assertEqual(urls(recommend_related(source, [global_item, *candidates])),
                                 urls(expected_order))

    def test_weight_science_and_program_fallback_relations_are_reciprocal(self):
        for left, right in [('weight-management', 'exercise-science'),
                            ('weight-management', 'workout-programs'),
                            ('workout-programs', 'exercise-science')]:
            self.assertIn(right, RELATED_CATEGORIES[left])
            self.assertIn(left, RELATED_CATEGORIES[right])
        source = article('source', category='weight-management', tags=['체성분'])
        direct = article('direct', category='combat-culture', tags=['체성분'])
        same = article('same', category='weight-management')
        science = article('science', category='exercise-science')
        program = article('program', category='workout-programs', published='2026-11-11')
        draft = article('draft', category='weight-management', tags=['체성분'], draft=True)
        self.assertEqual(urls(recommend_related(source, [science, draft, source, same, direct, program])),
                         urls([direct, same, program]))

    def test_global_fill_score_then_date_then_url_and_small_catalogs(self):
        source = article('source', title='리듬', category='combat-culture')
        candidates = [article('c', category='exercise-science', published='2026-11-02'),
                      article('b', category='exercise-science', published='2026-11-02'),
                      article('old', category='exercise-science', published='2020-01-01'),
                      article('score', category='exercise-science', title='리듬', published='2010-01-01')]
        expected = urls([candidates[3], candidates[1], candidates[0]])
        for ordering in permutations(candidates):
            self.assertEqual(urls(recommend_related(source, ordering)), expected)
        for size in range(3):
            self.assertEqual(len(recommend_related(source, candidates[:size])), size)

    def test_excludes_self_drafts_and_duplicate_urls_without_mutation(self):
        source = article('source', related=['/articles/draft.html'])
        public = [article('a'), article('b'), article('c')]
        draft = article('draft', draft=True, tags=['잽'])
        catalog = [source, draft, *public, dict(public[0]), dict(source)]
        before = repr(catalog)
        self.assertEqual(urls(recommend_related(source, catalog)), urls(public))
        self.assertEqual(urls(recommend_related(source, reversed(catalog))), urls(public))
        self.assertEqual(repr(catalog), before)
        self.assertEqual(recommend_related(draft, catalog), [])

    def test_related_has_no_influence_even_for_missing_or_invalid_urls(self):
        source = article('source')
        catalog = [article('a'), article('b'), article('c'), article('d')]
        expected = urls(recommend_related(source, catalog))
        for value in [None, [], ['/articles/d.html'], ['/missing.html'], 'obsolete',
                      ['/articles/source.html', '/articles/draft.html']]:
            source['related'] = value
            catalog[0]['related'] = value
            self.assertEqual(urls(recommend_related(source, catalog)), expected)

    def test_legacy_without_keywords_lead_or_draft_is_a_direct_candidate(self):
        legacy = article('legacy', title='샌드백 거리 조절', category='workout-programs')
        del legacy['keywords']
        source = article('source', keywords=['샌드백 거리 조절'])
        self.assertGreaterEqual(relevance_score(source, legacy), 8)
        self.assertEqual(recommend_related(source, [legacy]), [legacy])


class RecommendationBuildTests(unittest.TestCase):
    setUp = test_categories.CategoryTests.setUp

    def panel_urls(self, out, slug):
        html = (out / f'articles/{slug}.html').read_text(encoding='utf-8')
        panel = re.search(r'<div class="article-related-panel">(.*?)</div>', html, re.S)[1]
        links = re.findall(r'href="([^"]+)"', panel)
        self.assertEqual(links[-1], '/articles/index.html')
        self.assertEqual(len(links), 4)
        self.assertEqual(len(set(links)), 4)
        return links[:-1]

    def write_meta(self, path, meta, body):
        path.write_text('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)
                        + '---\n' + body, encoding='utf-8')

    def test_deprecated_related_is_ignored_without_url_or_type_validation(self):
        path = self.root / 'content/articles/boxing-heavy-bag-distance.md'
        _, front, body = path.read_text(encoding='utf-8').split('---', 2)
        meta = yaml.safe_load(front)
        out = build(self.root)
        expected = self.panel_urls(out, path.stem)
        # Omitted, dead/self/draft URLs and even old non-list values are inert.
        for value in [None, ['/missing.html', '/articles/boxing-first-class.html',
                              '/articles/boxing-heavy-bag-distance.html'], {'obsolete': True}]:
            if value is None:
                meta.pop('related', None)
            else:
                meta['related'] = value
            self.write_meta(path, meta, body)
            out = build(self.root)
            self.assertEqual(self.panel_urls(out, path.stem), expected)
        # Actual body links to drafts still fail; the existing content tests
        # exercise that policy independently of ignored front matter.

    def test_new_public_article_recomputes_existing_pages_and_stays_deterministic(self):
        path = self.root / 'content/articles/boxing-heavy-bag-distance.md'
        original = path.read_bytes()
        _, front, body = original.decode('utf-8').split('---', 2)
        meta = yaml.safe_load(front)
        out = build(self.root)
        before = self.panel_urls(out, path.stem)
        meta.update(slug='recommendation-new', published='2026-11-10', updated='2026-11-10',
                    canonical='https://redboxing-gym.github.io/articles/recommendation-new.html')
        meta.pop('related', None)
        new_path = path.with_name('recommendation-new.md')
        self.write_meta(new_path, meta, body)
        out = build(self.root)
        after = self.panel_urls(out, path.stem)
        self.assertNotEqual(after, before)
        self.assertEqual(after[0], '/articles/recommendation-new.html')
        self.assertEqual(path.read_bytes(), original)
        hashes = {p.relative_to(out): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in out.rglob('*') if p.is_file()}
        build(self.root)
        self.assertEqual(hashes, {p.relative_to(out): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in out.rglob('*') if p.is_file()})
        # With the new article unpublished, it disappears from old panels too.
        meta['draft'] = True
        self.write_meta(new_path, meta, body)
        out = build(self.root)
        self.assertEqual(self.panel_urls(out, path.stem), before)
        self.assertFalse((out / 'articles/recommendation-new.html').exists())

    def test_all_public_panels_and_legacy_bytes_are_preserved(self):
        out = build(self.root)
        manifest, legacy, articles = load_articles(self.root)
        public_urls = {a['url'] for a in legacy + articles if not a.get('draft', False)}
        for item in articles:
            if not item['draft']:
                related = self.panel_urls(out, item['slug'])
                self.assertNotIn(item['url'], related)
                self.assertTrue(set(related) <= public_urls)
        for path in manifest['protected']:
            self.assertEqual((out / path).read_bytes(), (self.root / path).read_bytes())


if __name__ == '__main__':
    unittest.main()
