"""Mutation tests for the checksummed external-skill vendor boundary."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "vendor" / "skill_vendor.py"
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def run_git(arguments: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        env=GIT_ENV,
        check=True,
        capture_output=True,
        text=True,
    )


def make_upstream(base: Path, skills: dict[str, str]) -> Path:
    upstream = base / "upstream"
    for name, description in skills.items():
        skill_dir = upstream / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
            encoding="utf-8",
        )
    run_git(["init", "--quiet"], upstream)
    run_git(["add", "-A"], upstream)
    run_git(["commit", "--quiet", "-m", "initial"], upstream)
    run_git(["tag", "-a", "v1.0.0", "-m", "release"], upstream)
    return upstream


def make_consumer(base: Path, upstream: Path, skills: list[str]) -> Path:
    consumer = base / "consumer"
    consumer.mkdir()
    (consumer / "skills").mkdir()
    lock = {
        "version": 1,
        "sources": [
            {
                "package": "demo-skills",
                "repo": str(upstream),
                "ref": "v1.0.0",
                "sha": "",
                "skills": skills,
                "dest": "skills/",
                "sha256": {},
            }
        ],
    }
    (consumer / "skills.lock.json").write_text(
        json.dumps(lock, indent=2) + "\n",
        encoding="utf-8",
    )
    (consumer / "plugin-local-skills.json").write_text(
        json.dumps({"version": 1, "dest": "skills/", "skills": []}, indent=2) + "\n",
        encoding="utf-8",
    )
    return consumer


def vendor(command: str, consumer: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), command, "--lock", "skills.lock.json", *extra],
        cwd=consumer,
        capture_output=True,
        text=True,
    )


class SkillVendorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_update_then_online_and_offline_check(self) -> None:
        upstream = make_upstream(
            self.base,
            {"demo-one": "first demo skill gate", "demo-two": "second demo skill gate"},
        )
        consumer = make_consumer(self.base, upstream, ["demo-one", "demo-two"])

        result = vendor("update", consumer)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        lock = json.loads((consumer / "skills.lock.json").read_text(encoding="utf-8"))
        source = lock["sources"][0]
        self.assertTrue(source["sha"])
        self.assertEqual({"demo-one", "demo-two"}, set(source["sha256"]))
        self.assertEqual(vendor("check", consumer, "--offline").returncode, 0)
        self.assertEqual(vendor("check", consumer).returncode, 0)

    def test_update_preserves_unmanaged_plugin_skill(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "managed external skill"})
        consumer = make_consumer(self.base, upstream, ["demo-one"])
        local = consumer / "skills" / "plugin-local"
        local.mkdir()
        (local / "SKILL.md").write_text(
            "---\nname: plugin-local\ndescription: plugin internal custom skill\n---\n",
            encoding="utf-8",
        )
        (consumer / "plugin-local-skills.json").write_text(
            json.dumps({"version": 1, "dest": "skills/", "skills": ["plugin-local"]}, indent=2)
            + "\n",
            encoding="utf-8",
        )

        self.assertEqual(vendor("update", consumer).returncode, 0)
        self.assertTrue((local / "SKILL.md").is_file())
        self.assertNotIn(
            "plugin-local",
            json.loads((consumer / "skills.lock.json").read_text())["sources"][0]["sha256"],
        )

    def test_update_rejects_undeclared_plugin_local_skill(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "managed external skill"})
        consumer = make_consumer(self.base, upstream, ["demo-one"])
        local = consumer / "skills" / "plugin-local"
        local.mkdir()
        (local / "SKILL.md").write_text(
            "---\nname: plugin-local\ndescription: undeclared local skill\n---\n",
            encoding="utf-8",
        )

        result = vendor("update", consumer)
        self.assertEqual(result.returncode, 1)
        self.assertIn("undeclared plugin-local skills", result.stdout)

    def test_update_accepts_dispatched_tag_and_expected_sha(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "first release"})
        consumer = make_consumer(self.base, upstream, ["demo-one"])
        self.assertEqual(vendor("update", consumer).returncode, 0)

        skill = upstream / "skills" / "demo-one" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "second release\n", encoding="utf-8")
        run_git(["add", "-A"], upstream)
        run_git(["commit", "--quiet", "-m", "second"], upstream)
        run_git(["tag", "-a", "v1.1.0", "-m", "second release"], upstream)
        expected_sha = subprocess.run(
            ["git", "rev-list", "-n", "1", "v1.1.0"],
            cwd=upstream,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        result = vendor(
            "update",
            consumer,
            "--source-ref",
            "demo-skills=v1.1.0",
            "--expected-sha",
            f"demo-skills={expected_sha}",
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        lock = json.loads((consumer / "skills.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["sources"][0]["ref"], "v1.1.0")
        self.assertEqual(lock["sources"][0]["sha"], expected_sha)
        self.assertIn("second release", (consumer / "skills" / "demo-one" / "SKILL.md").read_text())

    def test_update_rejects_dispatched_sha_mismatch_without_rewriting_lock(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "first release"})
        consumer = make_consumer(self.base, upstream, ["demo-one"])
        self.assertEqual(vendor("update", consumer).returncode, 0)
        before = (consumer / "skills.lock.json").read_text(encoding="utf-8")

        result = vendor(
            "update",
            consumer,
            "--source-ref",
            "demo-skills=v1.0.0",
            "--expected-sha",
            "demo-skills=0000000000000000000000000000000000000000",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected dispatched commit", result.stdout)
        self.assertEqual((consumer / "skills.lock.json").read_text(encoding="utf-8"), before)

    def test_check_detects_in_tree_tampering(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "first demo skill gate"})
        consumer = make_consumer(self.base, upstream, ["demo-one"])
        self.assertEqual(vendor("update", consumer).returncode, 0)
        target = consumer / "skills" / "demo-one" / "SKILL.md"
        target.write_text(target.read_text(encoding="utf-8") + "local edit\n", encoding="utf-8")

        result = vendor("check", consumer, "--offline")
        self.assertEqual(result.returncode, 1)
        self.assertIn("differs from the lockfile digest", result.stdout)

    def test_check_detects_upstream_tag_movement_and_update_resyncs(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "first demo skill gate"})
        consumer = make_consumer(self.base, upstream, ["demo-one"])
        self.assertEqual(vendor("update", consumer).returncode, 0)

        skill = upstream / "skills" / "demo-one" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "upstream change\n", encoding="utf-8")
        run_git(["add", "-A"], upstream)
        run_git(["commit", "--quiet", "-m", "change"], upstream)
        run_git(["tag", "-f", "-a", "v1.0.0", "-m", "moved release"], upstream)

        result = vendor("check", consumer)
        self.assertEqual(result.returncode, 1)
        self.assertIn("moved", result.stdout)
        self.assertEqual(vendor("update", consumer).returncode, 0)
        self.assertIn("upstream change", skill.read_text(encoding="utf-8"))

    def test_update_fails_when_skill_missing_upstream(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "first demo skill gate"})
        consumer = make_consumer(self.base, upstream, ["demo-one", "demo-ghost"])
        result = vendor("update", consumer)
        self.assertEqual(result.returncode, 1)
        self.assertIn("demo-ghost", result.stdout)

    def test_illegal_skill_name_is_rejected(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "first demo skill gate"})
        consumer = make_consumer(self.base, upstream, [".."])
        result = vendor("update", consumer)
        self.assertEqual(result.returncode, 1)
        self.assertIn("illegal skill name", result.stdout)

    def test_duplicate_skill_names_are_rejected(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "first demo skill gate"})
        consumer = make_consumer(self.base, upstream, ["demo-one", "demo-one"])
        result = vendor("update", consumer)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate skill names", result.stdout)

    def test_check_fails_when_managed_skill_is_deleted(self) -> None:
        upstream = make_upstream(self.base, {"demo-one": "first demo skill gate"})
        consumer = make_consumer(self.base, upstream, ["demo-one"])
        self.assertEqual(vendor("update", consumer).returncode, 0)
        shutil.rmtree(consumer / "skills" / "demo-one")

        result = vendor("check", consumer, "--offline")
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing from the tree", result.stdout)


if __name__ == "__main__":
    unittest.main()
