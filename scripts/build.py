"""Build an isolated static artifact; never rewrite legacy source files."""
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://redboxing-gym.github.io'
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'


def require(condition, message):
    if not condition:
        raise ValueError(message)


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key, value in node.value:
        key = loader.construct_object(key)
        require(key not in result, f'Duplicate metadata key: {key}')
        result[key] = loader.construct_object(value)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


YOUTUBE_TOKEN = re.compile(r'\[\[youtube:([A-Za-z0-9_-]{11})\]\]')


def render_article_body(source, filename):
    # No arbitrary HTML in Markdown; only validated YouTube video identifiers.
    require(not re.search(r'<\s*/?\s*[A-Za-z!]', source), f'{filename}: raw HTML is not supported')
    require('[[youtube:' not in YOUTUBE_TOKEN.sub('', source),
            f'{filename}: invalid YouTube shortcode')
    html = markdown.markdown(source, extensions=['tables', 'fenced_code', 'toc'])
    def embed(match):
        video_id = match.group(1)
        return ('<div class="article-video"><iframe '
                'src="https://www.youtube-nocookie.com/embed/' + video_id + '" '
                'title="공식 경기 영상" loading="lazy" '
                'referrerpolicy="strict-origin-when-cross-origin" '
                'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                'allowfullscreen></iframe></div>')
    # Replace a standalone shortcode paragraph with a valid block-level iframe.
    html = re.sub(r'<p>\s*(\[\[youtube:[A-Za-z0-9_-]{11}\]\])\s*</p>',
                  lambda m: embed(YOUTUBE_TOKEN.fullmatch(m.group(1))), html)
    return html


def load_articles(root):
    manifest = json.loads((root / 'content/legacy-articles.json').read_text(encoding='utf-8'))
    for path, digest in manifest['protected'].items():
        require((root / path).is_file(), f'Protected file missing: {path}')
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == digest,
                f'Protected file changed: {path}')
    legacy = manifest['articles']
    used = {a['url'] for a in legacy} | {'/articles/index.html'}
    articles = []
    for path in sorted((root / 'content/articles').glob('*.md')):
        source = path.read_text(encoding='utf-8')
        match = re.fullmatch(r'---\r?\n(.*?)\r?\n---\r?\n(.*)', source, re.S)
        require(match is not None, f'{path.name}: YAML front matter required')
        meta = yaml.load(match[1], Loader=UniqueLoader)
        require(isinstance(meta, dict), f'{path.name}: metadata must be a mapping')
        allowed = {'title', 'description', 'slug', 'published', 'updated', 'keywords',
                   'canonical', 'kicker', 'lead', 'hero_image', 'hero_alt', 'tags', 'related', 'draft'}
        require(not set(meta) - allowed, f'{path.name}: unknown metadata fields')
        for key in allowed - {'related', 'tags'}:
            require(key in meta, f'{path.name}: missing {key}')
        require(type(meta['draft']) is bool, f'{path.name}: draft must be true or false')
        for key in ['title', 'description', 'slug', 'canonical', 'kicker', 'lead', 'hero_image', 'hero_alt']:
            require(isinstance(meta[key], str) and meta[key].strip(), f'{path.name}: invalid {key}')
        require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', meta['slug']), f'{path.name}: invalid slug')
        require(path.stem == meta['slug'], f'{path.name}: filename must match slug')
        meta['url'] = f"/articles/{meta['slug']}.html"
        require(meta['url'] not in used, f'{path.name}: duplicate or reserved URL')
        require(not (root / meta['url'].lstrip('/')).exists(), f'{path.name}: existing HTML URL is reserved')
        used.add(meta['url'])
        require(meta['canonical'] == BASE + meta['url'], f'{path.name}: canonical must match URL')
        for key in ['published', 'updated']:
            value = str(meta[key])
            require(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), f'{path.name}: invalid {key}')
            date.fromisoformat(value)
            meta[key] = value
        require(meta['updated'] >= meta['published'], f'{path.name}: updated precedes published')
        for key in ['keywords', 'tags', 'related']:
            meta.setdefault(key, [])
            require(isinstance(meta[key], list) and all(isinstance(v, str) and v.strip() for v in meta[key]),
                    f'{path.name}: {key} must be a string list')
        require(meta['keywords'], f'{path.name}: keywords required')
        require(meta['hero_image'].startswith('/assets/img/') and '..' not in meta['hero_image'],
                f'{path.name}: invalid image path')
        require((root / meta['hero_image'].lstrip('/')).is_file(), f'{path.name}: image missing')
        # Raw HTML is outside the authoring contract; JSON-LD is generated by the template.
        require(not re.search(r'<\s*/?\s*[A-Za-z!]', match[2]), f'{path.name}: raw HTML is not supported')
        require(not re.search(r'^#\s', match[2], re.M), f'{path.name}: use H2 or lower')
        require(match[2].strip(), f'{path.name}: empty body')
        meta['body'] = render_article_body(match[2], path.name)
        articles.append(meta)
    return manifest, legacy, articles


def validate_templates(root):
    for path in sorted((root / 'templates').glob('*.html')):
        text = path.read_text(encoding='utf-8', errors='strict')
        # Templates contain labels, not prose questions; reject replacement runs
        # and question-mark words while allowing an ordinary final question mark.
        require('\ufffd' not in text and not re.search(r'\?{2,}|(?<!\S)\?(?=\s)', text),
                f'{path.name}: corrupted template text')




def build(root=ROOT):
    validate_templates(root)
    manifest, legacy, articles = load_articles(root)
    public = sorted([a for a in articles if not a['draft']], key=lambda a: (a['published'], a['slug']), reverse=True)
    catalog = legacy + public
    lookup = {a['url']: a for a in catalog}
    for a in articles:
        require(all(u in lookup and u != a['url'] for u in a['related']), f"{a['slug']}: invalid related URL")
    out = root / 'dist'
    # Only this fixed, verified directory is disposable.
    require(not out.is_symlink() and out.resolve() == root.resolve() / 'dist', 'Unsafe output directory')
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    for folder in ['assets', 'css', 'js', 'articles']:
        shutil.copytree(root / folder, out / folder)
    for path in ['index.html', 'robots.txt', 'sitemap.xml', 'sitemap-pages.xml',
                 'google23bb310db4f0bb3a.html', 'navera7eccb22797895e11709710faa396cbf.html']:
        shutil.copy2(root / path, out / path)
    env = Environment(loader=FileSystemLoader(root / 'templates'), undefined=StrictUndefined,
                      autoescape=select_autoescape(['html']))
    for a in public:
        explicit = [lookup[u] for u in a['related']]
        candidates = sorted((b for b in catalog if b['url'] != a['url']),
                            key=lambda b: (-len(set(a['tags']) & set(b['tags'])), b['url']))
        related = (explicit + [b for b in candidates if b not in explicit])[:3]
        schema = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'],
                  'description': a['description'], 'image': BASE + a['hero_image'],
                  'datePublished': a['published'], 'dateModified': a['updated'],
                  'author': {'@type': 'Organization', 'name': '레드복싱'},
                  'publisher': {'@type': 'Organization', 'name': '레드복싱'},
                  'mainEntityOfPage': {'@type': 'WebPage', '@id': a['canonical']}}
        html = env.get_template('article.html').render(a=a, related=related, schema=schema)
        (out / a['url'].lstrip('/')).write_text(html, encoding='utf-8')
    # Existing homepage cards and order remain byte-identical; add cards only in output.
    if public:
        home = (root / 'index.html').read_text(encoding='utf-8')
        marker = '        <!-- Branch / CTA-->'
        require(home.count(marker) == 1, 'Homepage insertion marker missing or ambiguous')
        before, after = home.split(marker)
        ending = re.search(r'(\s*</div>\s*</div>\s*</section>\s*)$', before)
        require(ending is not None, 'Homepage article section shape changed')
        cards = ''.join(env.get_template('article-card.html').render(a=a) for a in public)
        home = before[:ending.start()] + cards + ending[0] + marker + after
        (out / 'index.html').write_text(home, encoding='utf-8')
    (out / 'articles/index.html').write_text(env.get_template('article-list.html').render(articles=catalog), encoding='utf-8')
    for name in ['sitemap.xml', 'sitemap-pages.xml']:
        tree = ET.parse(root / name)
        existing = {node.find(f'{{{NS}}}loc').text for node in tree.getroot()}
        entry = ET.SubElement(tree.getroot(), f'{{{NS}}}url')
        ET.SubElement(entry, f'{{{NS}}}loc').text = BASE + '/articles/index.html'
        for a in public:
            require(a['canonical'] not in existing, f'Duplicate sitemap URL: {a["canonical"]}')
            entry = ET.SubElement(tree.getroot(), f'{{{NS}}}url')
            ET.SubElement(entry, f'{{{NS}}}loc').text = a['canonical']
            ET.SubElement(entry, f'{{{NS}}}lastmod').text = a['updated']
        ET.register_namespace('', NS)
        tree.write(out / name, encoding='utf-8', xml_declaration=True)
    (out / '.nojekyll').touch()
    from validate import validate
    validate(root, out, manifest, articles)
    print(f'PASS: {len(legacy)} legacy, {len(public)} published, {len(articles)-len(public)} drafts excluded')
    return out


if __name__ == '__main__':
    try:
        build()
    except (ValueError, yaml.YAMLError) as exc:
        print(f'BUILD FAILED: {exc}', file=sys.stderr)
        sys.exit(1)
