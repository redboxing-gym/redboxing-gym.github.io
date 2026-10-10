"""Compare PR with its base without interpolating untrusted shell commands."""
import json
import os
import subprocess

from build import ROOT, load_articles, require


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def check():
    manifest, _, current = load_articles(ROOT)
    base = os.environ.get('BASE_SHA') or manifest['baseline_commit']
    require(len(base) == 40 and all(c in '0123456789abcdef' for c in base), 'Invalid base SHA')
    require(manifest['baseline_commit'] == 'a5e9b1c67652d5d197e4134328ebfdb7e29d7a2d', 'Original baseline changed')
    protected = set(git('ls-tree', '-r', '--name-only', manifest['baseline_commit'], 'articles').decode('utf-8').splitlines())
    protected |= {'google23bb310db4f0bb3a.html', 'navera7eccb22797895e11709710faa396cbf.html'}
    require(set(manifest['protected']) == protected, 'Protected file inventory changed')
    for path in manifest['protected']:
        require(git('show', manifest['baseline_commit'] + ':' + path) == (ROOT / path).read_bytes(),
                f'Protected file differs from original Git baseline: {path}')
        require(git('show', base + ':' + path) == (ROOT / path).read_bytes(),
                f'Protected file changed in PR: {path}')
    files = git('ls-tree', '-r', '--name-only', base, 'content/articles').decode('utf-8').splitlines()
    by_slug = {a['slug']: a for a in current}
    import re
    import yaml
    for path in files:
        if not path.endswith('.md'):
            continue
        text = git('show', base + ':' + path).decode('utf-8')
        match = re.match(r'---\r?\n(.*?)\r?\n---', text, re.S)
        old = yaml.safe_load(match[1])
        if old.get('draft') is False:
            now = by_slug.get(old['slug'])
            require(now is not None and not now['draft'] and now['canonical'] == old['canonical']
                    and now['published'] == str(old['published']), f'Published URL/date removed or changed: {path}')
    print('PASS: PR preserves original files and published URLs')


if __name__ == '__main__':
    check()
