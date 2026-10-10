"""Shared policy for PRs, first deployment and later deployments.

draft:false in target first-parent history locks a URL even if deployment was
disabled. Intermediate states on side branches do not lock unpublished drafts.
Missing history fails closed; no HEAD^ or saved deployment state is needed.
"""
import argparse
import os
import re
import subprocess
from datetime import date

import yaml

from build import ROOT, UniqueLoader, load_articles, require

ORIGINAL_BASELINE = 'a5e9b1c67652d5d197e4134328ebfdb7e29d7a2d'


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def history_article(text):
    match = re.fullmatch(r'---\r?\n(.*?)\r?\n---\r?\n(.*)', text, re.S)
    require(match is not None, 'Historical Markdown has no valid front matter')
    meta = yaml.load(match[1], Loader=UniqueLoader)
    require(isinstance(meta, dict) and type(meta.get('draft')) is bool, 'Historical draft state is invalid')
    if meta['draft']:
        return None
    for key in ['slug', 'canonical', 'published', 'updated']:
        require(key in meta, f'Historical published article missing {key}')
    for key in ['published', 'updated']:
        value = str(meta[key])
        require(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), f'Historical {key} is invalid')
        date.fromisoformat(value)
        meta[key] = value
    return meta


def check(root=ROOT, mode='auto', base_sha=None, require_main_tip=False):
    manifest, _, current = load_articles(root)
    require(manifest['baseline_commit'] == ORIGINAL_BASELINE, 'Original baseline changed')
    base_sha = base_sha if base_sha is not None else os.environ.get('BASE_SHA')
    require(mode in {'auto', 'pr', 'deployment'}, 'Invalid policy mode')
    if mode == 'pr' or (mode == 'auto' and base_sha):
        require(isinstance(base_sha, str) and re.fullmatch(r'[0-9a-f]{40}', base_sha), 'Invalid or missing PR base SHA')
        reference = base_sha
    else:
        # First manual deployment and later main pushes inspect all main history.
        # Deployment ignores BASE_SHA so stale environment data cannot narrow it.
        reference = git(root, 'rev-parse', 'HEAD').decode().strip()
    if require_main_tip:
        require(mode == 'deployment', 'Main-tip guard is only valid in deployment mode')
        remote = git(root, 'ls-remote', 'origin', 'refs/heads/main').decode().strip().split()
        require(len(remote) == 2 and remote[1] == 'refs/heads/main' and remote[0] == reference,
                'Deployment checkout is not the current main tip; start a new main run')
    commits = git(root, 'rev-list', '--first-parent', reference).decode().splitlines()
    require(ORIGINAL_BASELINE in commits, 'Original baseline missing from first-parent history; fetch-depth: 0 required')
    commits = list(reversed(commits[:commits.index(ORIGINAL_BASELINE) + 1]))
    protected = set(git(root, 'ls-tree', '-r', '--name-only', ORIGINAL_BASELINE, 'articles').decode('utf-8').splitlines())
    protected |= {'google23bb310db4f0bb3a.html', 'navera7eccb22797895e11709710faa396cbf.html'}
    require(set(manifest['protected']) == protected, 'Protected file inventory changed')
    for path in manifest['protected']:
        require(git(root, 'show', ORIGINAL_BASELINE + ':' + path) == (root / path).read_bytes(),
                f'Protected file differs from original Git baseline: {path}')
    by_slug = {a['slug']: a for a in current}
    seen_blobs, published = set(), set()
    for commit in commits:
        entries = git(root, 'ls-tree', '-r', '--format=%(objectname) %(path)', commit, 'content/articles').decode('utf-8').splitlines()
        for entry in entries:
            blob, path = entry.split(' ', 1)
            if not path.endswith('.md') or blob in seen_blobs:
                continue
            seen_blobs.add(blob)
            old = history_article(git(root, 'cat-file', 'blob', blob).decode('utf-8'))
            if old is None:
                continue
            published.add(old['slug'])
            now = by_slug.get(old['slug'])
            require(now is not None and not now['draft'] and now['canonical'] == old['canonical']
                    and now['published'] == old['published'], f'Published URL/date removed or changed: {path}')
            require(now['updated'] >= old['updated'], f'Published modified date moved backwards: {path}')
    print(f'PASS: original files and {len(published)} published URL locks across {len(commits)} first-parent commits')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['auto', 'pr', 'deployment'], default='auto')
    parser.add_argument('--require-main-tip', action='store_true')
    args = parser.parse_args()
    check(mode=args.mode, require_main_tip=args.require_main_tip)
