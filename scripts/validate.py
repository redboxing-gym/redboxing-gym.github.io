"""Offline SEO and local-link validation; no third-party availability dependency."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from xml.etree import ElementTree as ET

from build import BASE, NS, ROOT, load_articles, require


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.canonicals, self.meta = [], set(), [], {}
        self.h1 = 0
        self.title = ''
        self.in_title = False
        self.in_json = False
        self.buffer = ''
        self.schemas = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            self.meta[a.get('name', a.get('property'))] = a.get('content')
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href'))
        for key in ['href', 'src', 'data-modal-target', 'data-bs-target']:
            if key in a:
                self.refs.append(a[key])
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.in_json, self.buffer = True, ''

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_json:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'script' and self.in_json:
            self.schemas.append(json.loads(self.buffer))
            self.in_json = False


def validate(root, out, manifest, articles):
    # Static deployment has no reason to contain source or build tooling.
    for path in out.rglob('*'):
        relative = path.relative_to(out)
        require(not path.is_symlink(), f'Deployment symlink forbidden: {relative}')
        require(relative.parts[0] not in {'content', 'scripts', 'templates', 'tests', 'docs', '.github', '.git'},
                f'Build source leaked into output: {relative}')
        require(path.suffix.lower() not in {'.md', '.py', '.yml', '.yaml'},
                f'Source file leaked into output: {relative}')
    for path, digest in manifest['protected'].items():
        require((out / path).is_file() and hashlib.sha256((out / path).read_bytes()).hexdigest() == digest,
                f'Protected output changed: {path}')
    pages = {p.relative_to(out).as_posix(): Page(p.read_text(encoding='utf-8')) for p in out.rglob('*.html')}
    canonicals = set()
    # Validate draft body resources without writing or adding draft pages to public output.
    checks = list(pages.items()) + [(a['url'].lstrip('/'), Page(a['body'])) for a in articles if a['draft']]
    for path, page in checks:
        for ref in page.refs:
            parsed = urlparse(urljoin(BASE + '/' + path, ref))
            require(parsed.scheme in {'https', 'http', 'tel', 'mailto'}, f'{path}: unsafe link {ref}')
            if parsed.netloc != urlparse(BASE).netloc:
                continue
            target = unquote(parsed.path).lstrip('/') or 'index.html'
            if path not in pages and target == path and parsed.fragment:
                require(unquote(parsed.fragment) in page.ids, f'{path}: broken draft anchor {ref}')
                continue
            file = (out / target).resolve()
            require(file.is_relative_to(out.resolve()), f'{path}: link escapes output')
            if file.is_dir():
                target = target.rstrip('/') + '/index.html'
                file = out / target
            require(file.is_file(), f'{path}: broken resource {ref}')
            if parsed.fragment and target in pages:
                require(unquote(parsed.fragment) in pages[target].ids, f'{path}: broken anchor {ref}')
        if page.canonicals:
            require(len(page.canonicals) == 1, f'{path}: multiple canonicals')
            canonical = page.canonicals[0]
            require(canonical not in canonicals, f'{path}: duplicate canonical')
            canonicals.add(canonical)
            require(canonical == BASE + ('/' if path == 'index.html' else '/' + path), f'{path}: canonical mismatch')
            require(page.title.strip() and page.meta.get('description'), f'{path}: missing SEO text')
            require(page.meta.get('og:url') == canonical, f'{path}: og:url mismatch')
            require(page.h1 == 1, f'{path}: expected one H1')
    for a in articles:
        path = a['url'].lstrip('/')
        if a['draft']:
            require(not (out / path).exists(), f'Draft HTML leaked: {path}')
            require(all(a['url'] not in p.refs and a['canonical'] not in p.refs for p in pages.values()),
                    f'Draft link leaked: {path}')
            continue
        page = pages[path]
        require(page.canonicals == [a['canonical']], f'{path}: missing canonical')
        for key in ['keywords', 'og:title', 'og:description', 'og:image', 'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']:
            require(page.meta.get(key), f'{path}: missing {key}')
        require(len(page.schemas) == 1 and page.schemas[0].get('@type') == 'Article', f'{path}: Article schema missing')
        schema = page.schemas[0]
        require(schema['datePublished'] == a['published'] and schema['dateModified'] == a['updated']
                and schema['mainEntityOfPage']['@id'] == a['canonical'], f'{path}: schema mismatch')
        require(a['url'] in pages['index.html'].refs and a['url'] in pages['articles/index.html'].refs,
                f'{path}: missing listing link')
    expected = {BASE + '/', BASE + '/articles/index.html', *[BASE + a['url'] for a in manifest['articles']],
                *[a['canonical'] for a in articles if not a['draft']]}
    for name in ['sitemap.xml', 'sitemap-pages.xml']:
        entries = ET.parse(out / name).getroot().findall(f'{{{NS}}}url')
        urls = [n.find(f'{{{NS}}}loc').text for n in entries]
        require(len(urls) == len(set(urls)) and set(urls) == expected, f'{name}: sitemap URL mismatch')
    print(f'PASS: SEO, structured data, protected bytes, resources, anchors and sitemaps ({len(pages)} HTML files)')


if __name__ == '__main__':
    manifest, _, articles = load_articles(ROOT)
    validate(ROOT, ROOT / 'dist', manifest, articles)
