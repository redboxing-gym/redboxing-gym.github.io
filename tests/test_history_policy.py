"""Exercise real temporary Git graphs instead of mocking Git history."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_changes
from build import ROOT


class HistoryPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {'BASE_SHA': ''})
        self.env.start()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Policy Test')
        self.git('config', 'user.email', 'policy@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.git('remote', 'add', 'origin', self.root.as_uri())
        manifest = json.loads((ROOT / 'content/legacy-articles.json').read_text(encoding='utf-8'))
        for path in manifest['protected']:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        image = self.root / 'assets/img/freetime.webp'
        image.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / 'assets/img/freetime.webp', image)
        self.baseline = self.commit('Original static site')
        manifest['baseline_commit'] = self.baseline
        (self.root / 'content/articles').mkdir(parents=True)
        (self.root / 'content/legacy-articles.json').write_text(json.dumps(manifest), encoding='utf-8')
        self.article = self.root / 'content/articles/boxing-first-class.md'
        self.article.write_text((ROOT / 'content/articles/boxing-first-class.md').read_text(encoding='utf-8'), encoding='utf-8')
        self.commit('Introduce draft')
        self.baseline_patch = patch.object(check_changes, 'ORIGINAL_BASELINE', self.baseline)
        self.baseline_patch.start()

    def tearDown(self):
        self.baseline_patch.stop()
        self.env.stop()
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.PIPE).decode('utf-8').strip()

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def change(self, old, new):
        self.article.write_text(self.article.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')

    def publish(self):
        self.change('draft: true', 'draft: false')
        return self.commit('Publish article')

    def policy(self, mode='deployment', base_sha=None, require_main_tip=False):
        check_changes.check(self.root, mode=mode, base_sha=base_sha, require_main_tip=require_main_tip)

    def test_first_manual_and_repeat_deployment_use_all_history(self):
        self.publish()
        for index in range(3):
            (self.root / 'notes.txt').write_text(str(index))
            self.commit('Unrelated later change')
        self.policy()
        self.policy()
        self.change('draft: false', 'draft: true')
        self.commit('Attempt unpublish before first deployment')
        (self.root / 'notes.txt').write_text('later')
        self.commit('Later unrelated commit')
        with self.assertRaisesRegex(ValueError, 'Published URL/date'):
            self.policy()

    def test_multiple_rebased_commits_cannot_hide_a_url_change(self):
        self.publish()
        self.git('switch', '-c', 'rename-topic')
        self.article.rename(self.article.with_name('boxing-renamed.md'))
        self.article = self.article.with_name('boxing-renamed.md')
        self.change('boxing-first-class', 'boxing-renamed')
        self.commit('Rename URL in first commit of push')
        (self.root / 'notes.txt').write_text('second')
        self.commit('Second commit hides change from HEAD-parent comparison')
        self.git('switch', 'main')
        (self.root / 'main-notes.txt').write_text('main advanced')
        base = self.commit('Concurrent main change')
        self.git('switch', 'rename-topic')
        self.git('rebase', 'main')
        with self.assertRaisesRegex(ValueError, 'Published URL/date'):
            self.policy(mode='pr', base_sha=base)
        self.git('switch', 'main')
        self.git('merge', '--ff-only', 'rename-topic')
        with self.assertRaisesRegex(ValueError, 'Published URL/date'):
            self.policy()

    def test_multi_commit_merge_and_squash_allow_content_edits(self):
        self.publish()
        for squash in [False, True]:
            with self.subTest(squash=squash):
                base = self.git('rev-parse', 'HEAD')
                branch = 'edit-' + str(squash).lower()
                self.git('switch', '-c', branch)
                self.article.write_text(self.article.read_text(encoding='utf-8') + '\n추가 안내 문단입니다.\n', encoding='utf-8')
                self.commit('Edit published body on same day')
                (self.root / 'notes.txt').write_text(branch)
                self.commit('Second PR commit')
                self.policy(mode='pr', base_sha=base)
                self.git('switch', 'main')
                if squash:
                    self.git('merge', '--squash', branch)
                    self.commit('Squash edit PR')
                else:
                    self.git('merge', '--no-ff', branch, '-m', 'Merge edit PR')
                self.policy()

    def test_side_branch_intermediate_public_state_is_not_a_lock(self):
        base = self.git('rev-parse', 'HEAD')
        self.git('switch', '-c', 'draft-work')
        self.publish()
        self.change('draft: false', 'draft: true')
        self.commit('Keep final PR as draft')
        self.policy(mode='pr', base_sha=base)
        self.git('switch', 'main')
        self.git('merge', '--no-ff', 'draft-work', '-m', 'Merge final draft')
        self.policy()

    def test_merge_and_squash_reject_illegal_final_state_even_if_pr_was_bypassed(self):
        self.publish()
        for squash in [False, True]:
            with self.subTest(squash=squash):
                base = self.git('rev-parse', 'HEAD')
                branch = 'illegal-' + str(squash).lower()
                self.git('switch', '-c', branch)
                self.change('draft: false', 'draft: true')
                self.commit('Illegal unpublish')
                (self.root / 'notes.txt').write_text(branch)
                self.commit('Later housekeeping')
                with self.assertRaisesRegex(ValueError, 'Published URL/date'):
                    self.policy(mode='pr', base_sha=base)
                self.git('switch', 'main')
                if squash:
                    self.git('merge', '--squash', branch)
                    self.commit('Simulate bypassed squash in temporary repository')
                else:
                    self.git('merge', '--no-ff', branch, '-m', 'Simulate bypassed merge in temporary repository')
                with self.assertRaisesRegex(ValueError, 'Published URL/date'):
                    self.policy()
                self.change('draft: true', 'draft: false')
                self.commit('Restore public state for next scenario')
                self.policy()

    def test_public_identity_changes_fail_in_pr_and_deployment(self):
        base = self.publish()
        original = self.article.read_text(encoding='utf-8')
        for mutation in ['delete', 'draft', 'published', 'canonical']:
            for mode in ['pr', 'deployment']:
                with self.subTest(mutation=mutation, mode=mode):
                    self.article.write_text(original, encoding='utf-8')
                    if mutation == 'delete':
                        self.article.unlink()
                    elif mutation == 'draft':
                        self.change('draft: false', 'draft: true')
                    elif mutation == 'published':
                        self.change('published: "2026-10-10"', 'published: "2026-10-09"')
                    else:
                        self.change('canonical: "https://redboxing-gym.github.io/', 'canonical: "https://example.com/')
                    with self.assertRaises(ValueError):
                        self.policy(mode=mode, base_sha=base)
        self.article.write_text(original, encoding='utf-8')

    def test_metadata_edit_allowed_but_updated_cannot_regress(self):
        base = self.publish()
        self.change('updated: "2026-10-10"', 'updated: "2026-10-11"')
        self.change('첫 수업 준비', '첫 수업과 준비물')
        self.policy(mode='pr', base_sha=base)
        self.commit('Allowed content edit')
        self.policy()
        self.change('updated: "2026-10-11"', 'updated: "2026-10-10"')
        for mode in ['pr', 'deployment']:
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(ValueError, 'modified date moved backwards'):
                    self.policy(mode=mode, base_sha=self.git('rev-parse', 'HEAD'))

    def test_legacy_protection_in_both_modes(self):
        base = self.git('rev-parse', 'HEAD')
        for path in ['articles/boxing-diet-beginner.html', 'google23bb310db4f0bb3a.html']:
            original = (self.root / path).read_bytes()
            (self.root / path).write_bytes(original + b'changed')
            for mode in ['pr', 'deployment']:
                with self.subTest(path=path, mode=mode):
                    with self.assertRaisesRegex(ValueError, 'Protected file changed'):
                        self.policy(mode=mode, base_sha=base)
            (self.root / path).write_bytes(original)

    def test_stale_environment_cannot_narrow_deployment_history(self):
        old = self.git('rev-parse', 'HEAD')
        self.publish()
        self.change('draft: false', 'draft: true')
        with patch.dict(os.environ, {'BASE_SHA': old}):
            with self.assertRaisesRegex(ValueError, 'Published URL/date'):
                self.policy()

    def test_old_workflow_rerun_is_rejected_after_main_advances(self):
        old = self.publish()
        self.policy(require_main_tip=True)
        (self.root / 'notes.txt').write_text('new main revision')
        self.commit('Advance main')
        self.policy(require_main_tip=True)
        self.git('switch', '--detach', old)
        with self.assertRaisesRegex(ValueError, 'not the current main tip'):
            self.policy(require_main_tip=True)

    def test_missing_baseline_and_invalid_pr_reference_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'Invalid or missing PR base SHA'):
            self.policy(mode='pr', base_sha='')
        with patch.object(check_changes, 'ORIGINAL_BASELINE', '0' * 40):
            manifest = self.root / 'content/legacy-articles.json'
            data = json.loads(manifest.read_text(encoding='utf-8'))
            data['baseline_commit'] = '0' * 40
            manifest.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'missing from first-parent history'):
                self.policy()

    def test_shallow_clone_cannot_silently_drop_protection_history(self):
        with tempfile.TemporaryDirectory() as clone_root:
            shallow = Path(clone_root) / 'shallow'
            self.git('-c', 'core.autocrlf=false', 'clone', '--depth', '1', self.root.as_uri(), str(shallow))
            with self.assertRaisesRegex(ValueError, 'missing from first-parent history'):
                check_changes.check(shallow, mode='deployment')


if __name__ == '__main__':
    unittest.main()
