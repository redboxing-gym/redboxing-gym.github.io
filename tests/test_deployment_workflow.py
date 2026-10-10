"""Static safety tests; never request live Pages permissions or deployment."""
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class DeploymentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workflow = yaml.load((ROOT / '.github/workflows/pages-deploy.yml').read_text(encoding='utf-8'), Loader=yaml.BaseLoader)

    def test_main_only_and_explicit_activation(self):
        events = self.workflow['on']
        self.assertEqual(set(events), {'push', 'workflow_dispatch'})
        self.assertEqual(events['push']['branches'], ['main'])
        self.assertEqual(set(self.workflow['jobs']), {'build', 'deploy'})
        for job in self.workflow['jobs'].values():
            self.assertEqual(job['if'], "github.ref == 'refs/heads/main' && vars.PAGES_ACTIONS_ENABLED == 'true'")

    def test_only_dist_is_uploaded(self):
        steps = self.workflow['jobs']['build']['steps']
        uploads = [s for s in steps if 'upload' in s.get('uses', '')]
        self.assertEqual(len(uploads), 1)
        self.assertEqual(uploads[0]['uses'], 'actions/upload-pages-artifact@v4')
        self.assertEqual(uploads[0]['with'], {'path': 'dist/', 'retention-days': '1'})
        runs = [s['run'] for s in steps if 'run' in s]
        self.assertIn('python scripts/build.py', runs)
        self.assertIn('python scripts/validate.py', runs)
        self.assertIn('python -m unittest discover -s tests -v', runs)
        self.assertTrue(any('python scripts/check_changes.py' in r for r in runs))
        self.assertLess(next(i for i, s in enumerate(steps) if s.get('run') == 'python scripts/validate.py'),
                        next(i for i, s in enumerate(steps) if s in uploads))

    def test_write_permissions_only_in_deployment(self):
        self.assertEqual(self.workflow['permissions'], {'contents': 'read'})
        jobs = self.workflow['jobs']
        self.assertEqual(jobs['build']['permissions'], {'contents': 'read', 'pages': 'read'})
        self.assertEqual(jobs['deploy']['permissions'], {'pages': 'write', 'id-token': 'write'})
        self.assertEqual(jobs['deploy']['needs'], 'build')
        self.assertEqual(jobs['deploy']['environment']['name'], 'github-pages')
        self.assertEqual(len(jobs['deploy']['steps']), 1)
        self.assertEqual(jobs['deploy']['steps'][0]['uses'], 'actions/deploy-pages@v4')
        config = next(s for s in jobs['build']['steps'] if s.get('uses') == 'actions/configure-pages@v5')
        self.assertEqual(config['with']['enablement'], 'false')

    def test_free_runner_and_bounded_execution(self):
        for job in self.workflow['jobs'].values():
            self.assertEqual(job['runs-on'], 'ubuntu-latest')
            self.assertEqual(job['timeout-minutes'], '10')
        self.assertEqual(self.workflow['concurrency']['cancel-in-progress'], 'false')


if __name__ == '__main__':
    unittest.main()
