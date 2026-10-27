import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import ROOT, build, load_articles
from validate import validate


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ['assets', 'css', 'js', 'articles', 'content', 'templates']:
            shutil.copytree(ROOT / name, self.root / name)
        for path in ROOT.glob('*.html'):
            shutil.copy2(path, self.root / path.name)
        for name in ['robots.txt', 'sitemap.xml', 'sitemap-pages.xml']:
            shutil.copy2(ROOT / name, self.root / name)
        self.draft = self.root / 'content/articles/boxing-first-class.md'

    def tearDown(self):
        self.temp.cleanup()

    def change(self, before, after):
        self.draft.write_text(self.draft.read_text(encoding='utf-8').replace(before, after), encoding='utf-8')

    def test_draft_never_emitted_and_stale_output_removed(self):
        # Capture the baseline with any already-published articles present.
        baseline = build(self.root)
        expected_home = (baseline / 'index.html').read_bytes()
        self.change('draft: true', 'draft: false')
        out = build(self.root)
        self.assertTrue((out / 'articles/boxing-first-class.html').exists())
        self.change('draft: false', 'draft: true')
        out = build(self.root)
        self.assertFalse((out / 'articles/boxing-first-class.html').exists())
        for name in ['index.html', 'articles/index.html', 'sitemap.xml', 'sitemap-pages.xml']:
            self.assertNotIn('/articles/boxing-first-class.html', (out / name).read_text(encoding='utf-8'))
        self.assertEqual(expected_home, (out / 'index.html').read_bytes())

    def test_published_links_seo_and_determinism(self):
        self.change('draft: true', 'draft: false')
        original = self.draft.read_text(encoding='utf-8')
        (self.draft.parent / 'boxing-second-class.md').write_text(original.replace('boxing-first-class', 'boxing-second-class'), encoding='utf-8')
        out = build(self.root)
        first = {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
        html = (out / 'articles/boxing-first-class.html').read_text(encoding='utf-8')

        # 두 테스트 아티클이 모두 생성됐는지 확인
        self.assertTrue((out / 'articles/boxing-first-class.html').is_file())
        self.assertTrue((out / 'articles/boxing-second-class.html').is_file())

        # 명시적으로 지정한 관련 글 링크 확인
        self.assertIn('href="/articles/boxing-diet-beginner.html"', html)
        build(self.root)
        self.assertEqual(first, {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()})

    def test_legacy_bytes_protected(self):
        path = self.root / 'articles/boxing-diet-beginner.html'
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'Protected file changed'):
            build(self.root)

    def test_canonical_collision_and_path_traversal(self):
        for before, after in [('boxing-first-class', 'boxing-diet-beginner'), ('boxing-first-class', '../escape')]:
            with self.subTest(after=after):
                source = self.draft.read_text(encoding='utf-8')
                self.change(before, after)
                with self.assertRaises(ValueError):
                    build(self.root)
                self.draft.write_text(source, encoding='utf-8')

    def test_invalid_metadata_and_raw_html(self):
        source = self.draft.read_text(encoding='utf-8')
        for before, after in [('draft: true', 'draft: "true"'), ('draft: true', 'draft: true\ndraft: false'),
                              ('2026-10-10', '2026-99-99'), ('## 첫 수업 준비', '<script>alert(1)</script>'),
                              ('## 첫 수업 준비', '# duplicate H1'), ('/assets/img/freetime.webp', '/assets/img/missing.webp'),
                              ('canonical: "https://redboxing-gym.github.io/articles/boxing-first-class.html"', 'canonical: "https://example.com/"')]:
            with self.subTest(after=after):
                self.change(before, after)
                with self.assertRaises(ValueError):
                    build(self.root)
                self.draft.write_text(source, encoding='utf-8')

    def test_duplicate_slug(self):
        (self.draft.parent / 'duplicate.md').write_bytes(self.draft.read_bytes())
        with self.assertRaises(ValueError):
            build(self.root)

    def test_draft_body_broken_link_is_rejected(self):
        self.draft.write_text(self.draft.read_text(encoding='utf-8') + '\n[broken](/missing.html)\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'broken resource'):
            build(self.root)

    def test_template_encoding_and_corruption_guard(self):
        expected = {'article.html': ['레드복싱', '작성', '수정', '관련 글', '전체 글 보기'],
                    'article-list.html': ['복싱 운동 가이드', '레드복싱'],
                    'article-card.html': ['아티클 보기']}
        for name, labels in expected.items():
            path = self.root / 'templates' / name
            original = path.read_text(encoding='utf-8', errors='strict')
            for label in labels:
                self.assertIn(label, original)
            for broken in ['??', '????', '? ? ??', '\ufffd']:
                with self.subTest(template=name, broken=broken):
                    path.write_text(original.replace(labels[0], broken), encoding='utf-8')
                    with self.assertRaisesRegex(ValueError, 'corrupted template text'):
                        build(self.root)
                    path.write_text(original, encoding='utf-8')

    def test_links_anchors_and_unsafe_protocol(self):
        self.change('draft: true', 'draft: false')
        source = self.draft.read_text(encoding='utf-8')
        for link in ['/missing.html', '/index.html#missing', 'javascript:alert%281%29', '/articles/boxing-first-class.html#missing']:
            with self.subTest(link=link):
                self.draft.write_text(source + '\n[broken](' + link + ')\n', encoding='utf-8')
                with self.assertRaises(ValueError):
                    build(self.root)

    def test_published_cannot_link_to_draft(self):
        source = self.draft.read_text(encoding='utf-8').replace('boxing-first-class', 'boxing-second-class').replace('draft: true', 'draft: false')
        (self.draft.parent / 'boxing-second-class.md').write_text(source + '\n[draft](/articles/boxing-first-class.html)\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'broken resource'):
            build(self.root)

    def test_output_tampering_is_detected(self):
        out = build(self.root)
        (out / 'google23bb310db4f0bb3a.html').write_text('tampered', encoding='utf-8')
        manifest, _, articles = load_articles(self.root)
        with self.assertRaisesRegex(ValueError, 'Protected output changed'):
            validate(self.root, out, manifest, articles)

    def test_deployment_excludes_source_files(self):
        out = build(self.root)
        manifest, _, articles = load_articles(self.root)
        for path in ['scripts/build.py', 'content/articles/raw.md', 'templates/article.html',
                     'tests/test_content.py', 'assets/source.md']:
            with self.subTest(path=path):
                leaked = out / path
                leaked.parent.mkdir(parents=True, exist_ok=True)
                leaked.write_text('source', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'leaked into output'):
                    validate(self.root, out, manifest, articles)
                leaked.unlink()
                # The forbidden directory must also be absent from the artifact.
                if path.split('/')[0] in {'scripts', 'content', 'templates', 'tests'}:
                    shutil.rmtree(out / path.split('/')[0])


if __name__ == '__main__':
    unittest.main()
