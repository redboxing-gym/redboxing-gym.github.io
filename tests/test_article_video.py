"""Video shortcode parsing tests; no network calls."""
import unittest
from scripts.build import render_article_body


class ArticleVideoTests(unittest.TestCase):
    def test_valid_youtube_shortcode(self):
        html = render_article_body('## 영상\n\n[[youtube:abcdefghijk]]', 'test.md')
        self.assertIn('https://www.youtube-nocookie.com/embed/abcdefghijk', html)
        self.assertIn('class="article-video"', html)
        self.assertIn('<h2 ', html)
        self.assertNotIn('<p><div', html)

    def test_invalid_video_id(self):
        with self.assertRaises(ValueError):
            render_article_body('[[youtube:invalid]]', 'test.md')

    def test_raw_html_rejected(self):
        with self.assertRaises(ValueError):
            render_article_body('<iframe src="https://example.com"></iframe>', 'test.md')

    def test_ordinary_markdown(self):
        html = render_article_body('**복싱**', 'test.md')
        self.assertIn('<strong>복싱</strong>', html)


if __name__ == '__main__':
    unittest.main()
