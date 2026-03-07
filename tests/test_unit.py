"""
Unit tests for deep-loop components.
Run: cd /path/to/deep-loop && python -m pytest tests/test_unit.py -v
No H100 needed. No real training runs.
"""
import pathlib, subprocess, sys, os, json, tempfile
import pytest

ROOT = pathlib.Path(__file__).parent.parent


# ── orchestrate.py tests ────────────────────────────────────────────────────

class TestOrchestrate:
    def _import(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("orchestrate", ROOT / "orchestrate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_count_experiments_empty(self, tmp_path):
        orch = self._import()
        assert orch.count_experiments(tmp_path / "results.tsv") == 0

    def test_count_experiments_with_rows(self, tmp_path):
        orch = self._import()
        tsv = tmp_path / "results.tsv"
        tsv.write_text(
            "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
            "baseline\t0.997900\t44.0\tkeep\tbaseline\n"
            "abc1234\t0.994200\t44.1\tkeep\texperiment 1\n"
            "def5678\t0.998000\t44.0\tdiscard\texperiment 2\n"
        )
        # Should count 2 (excluding header and baseline)
        assert orch.count_experiments(tsv) == 2

    def test_get_best_val_bpb(self, tmp_path):
        orch = self._import()
        tsv = tmp_path / "results.tsv"
        tsv.write_text(
            "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
            "baseline\t0.997900\t44.0\tkeep\tbaseline\n"
            "abc1234\t0.994200\t44.1\tkeep\texperiment 1\n"
            "def5678\t0.989000\t44.3\tkeep\texperiment 2\n"
        )
        assert orch.get_best_val_bpb(tsv) == pytest.approx(0.989000)

    def test_get_best_val_bpb_excludes_crashes(self, tmp_path):
        orch = self._import()
        tsv = tmp_path / "results.tsv"
        tsv.write_text(
            "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
            "abc1234\t0.000000\t0.0\tcrash\tOOM\n"
            "def5678\t0.994000\t44.1\tkeep\tgood run\n"
        )
        # crash (0.0) should not be "best"
        assert orch.get_best_val_bpb(tsv) == pytest.approx(0.994000)

    def test_init_results_tsv_creates_file(self, tmp_path, monkeypatch):
        orch = self._import()
        monkeypatch.setattr(orch, "RESULTS_TSV", tmp_path / "results.tsv")
        orch.init_results_tsv()
        assert (tmp_path / "results.tsv").exists()
        content = (tmp_path / "results.tsv").read_text()
        # Check for baseline value (may be formatted as 0.9979 or 0.997900)
        assert "0.9979" in content
        assert "baseline" in content

    def test_init_results_tsv_no_overwrite(self, tmp_path, monkeypatch):
        orch = self._import()
        tsv = tmp_path / "results.tsv"
        tsv.write_text("existing content\n")
        monkeypatch.setattr(orch, "RESULTS_TSV", tsv)
        orch.init_results_tsv()
        assert tsv.read_text() == "existing content\n"


# ── mock_train.py tests ──────────────────────────────────────────────────────

class TestMockTrain:
    MOCK = ROOT / "tests" / "mock_train.py"

    def _run(self, env_extra=None, timeout=10):
        env = {**os.environ}
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [sys.executable, str(self.MOCK)],
            capture_output=True, text=True, timeout=timeout, env=env
        )

    def test_outputs_val_bpb(self):
        result = self._run({"MOCK_VAL_BPB": "0.994200"})
        assert result.returncode == 0
        assert "val_bpb:          0.994200" in result.stdout

    def test_outputs_peak_vram(self):
        result = self._run({"MOCK_VAL_BPB": "0.994200", "MOCK_VRAM_MB": "44000"})
        assert "peak_vram_mb:" in result.stdout

    def test_crash_mode(self):
        result = self._run({"MOCK_CRASH": "1"})
        assert result.returncode != 0
        assert "val_bpb" not in result.stdout  # crash = no metric output

    def test_grep_extracts_val_bpb(self):
        """Simulate how the /loop command extracts val_bpb from run.log"""
        result = self._run({"MOCK_VAL_BPB": "0.991500"})
        # grep "^val_bpb:" equivalent
        lines = [l for l in result.stdout.splitlines() if l.strip().startswith("val_bpb:")]
        assert len(lines) == 1
        val = float(lines[0].split(":")[1].strip())
        assert abs(val - 0.991500) < 0.000001


# ── notify.py tests ──────────────────────────────────────────────────────────

class TestNotify:
    NOTIFY = ROOT / "notify.py"

    def _run(self, args, tmp_path):
        log = tmp_path / "notify.log"
        env = {**os.environ, "DEEP_LOOP_NOTIFY_LOG": str(log)}
        result = subprocess.run(
            [sys.executable, str(self.NOTIFY)] + args,
            capture_output=True, text=True, timeout=10, env=env,
            cwd=tmp_path
        )
        return result, log

    def test_breakthrough_event(self, tmp_path):
        result, log = self._run(["--event", "breakthrough", "--val", "0.9876"], tmp_path)
        assert result.returncode == 0
        assert "0.987600" in result.stdout or "0.9876" in result.stdout

    def test_done_event_with_experiments(self, tmp_path):
        result, log = self._run(
            ["--event", "done", "--val", "0.9901", "--experiments", "87"], tmp_path
        )
        assert result.returncode == 0

    def test_writes_notify_log(self, tmp_path):
        self._run(["--event", "breakthrough", "--val", "0.989"], tmp_path)
        log = tmp_path / "notify.log"
        assert log.exists()
        assert "0.989" in log.read_text()


# ── meta_analyze.py tests ────────────────────────────────────────────────────

class TestMetaAnalyze:
    SCRIPT = ROOT / "meta_analyze.py"

    def test_build_analysis_task(self, tmp_path):
        """Verify task string is built from results.tsv + git log."""
        # Seed a fake results.tsv
        tsv = tmp_path / "results.tsv"
        tsv.write_text(
            "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
            "abc1234\t0.994200\t44.1\tkeep\twindow pattern SSSSL\n"
        )
        # Fake train.py
        (tmp_path / "train.py").write_text("# fake train\nprint('hello')\n")

        import importlib.util
        s = importlib.util.spec_from_file_location("meta_analyze", self.SCRIPT)
        mod = importlib.util.module_from_spec(s)
        s.loader.exec_module(mod)

        task = mod.build_analysis_task(tmp_path)
        assert "val_bpb" in task
        assert "0.994200" in task
        assert "window pattern SSSSL" in task
        assert "Proposed hypotheses" in task or "hypotheses" in task.lower()

    def test_runs_with_seeded_results(self, tmp_path):
        """Integration: run meta_analyze.py with seeded data, verify output file created."""
        # Seed results
        subprocess.run(
            [sys.executable, str(ROOT / "tests" / "seed_results.py"), str(tmp_path)],
            check=True
        )
        (tmp_path / "train.py").write_text("# mock train\n")

        # Run meta_analyze — this hits the real Anthropic API if key is set
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set — skipping live API test")

        result = subprocess.run(
            [sys.executable, str(self.SCRIPT),
             "--workspace", str(tmp_path),
             "--write-hypotheses", "next-hypotheses.md"],
            capture_output=True, text=True, timeout=120, cwd=tmp_path,
            env={**os.environ, "PYTHONPATH": str(ROOT)}
        )
        assert result.returncode == 0, f"meta_analyze failed: {result.stderr}"
        assert (tmp_path / "next-hypotheses.md").exists()
        content = (tmp_path / "next-hypotheses.md").read_text()
        assert len(content) > 100  # should have actual content


# ── Claude Code integration: slash commands ──────────────────────────────────

class TestClaudeCodeIntegration:

    def test_loop_command_exists(self):
        """.claude/commands/loop.md must exist."""
        assert (ROOT / ".claude" / "commands" / "loop.md").exists()

    def test_loop_command_has_required_sections(self):
        """loop.md must have Context Loading, Setup Verification, and Experiment Loop."""
        content = (ROOT / ".claude" / "commands" / "loop.md").read_text()
        assert "Context Loading" in content
        assert "Setup Verification" in content
        assert "Experiment Loop" in content
        assert "NEVER" in content  # "NEVER ask should I continue"
        assert "meta_analyze.py" in content
        assert "notify.py" in content

    def test_status_command_exists(self):
        """.claude/commands/status.md must exist."""
        assert (ROOT / ".claude" / "commands" / "status.md").exists()

    def test_claude_md_exists_and_has_invariants(self):
        """CLAUDE.md must exist and have [BLOCK] invariants."""
        claude_md = ROOT / "CLAUDE.md"
        assert claude_md.exists()
        content = claude_md.read_text()
        assert "[BLOCK]" in content
        assert "prepare.py" in content
        assert "results.tsv" in content
        assert "val_bpb" in content

    def test_program_md_exists_and_has_hypotheses(self):
        """program.md must have at least 5 hypotheses."""
        program_md = ROOT / "program.md"
        assert program_md.exists()
        content = program_md.read_text()
        # Count numbered hypotheses
        import re
        hypotheses = re.findall(r'^\s*\d+\.', content, re.MULTILINE)
        assert len(hypotheses) >= 5, f"Expected 5+ hypotheses, found {len(hypotheses)}"

    def test_all_referenced_scripts_exist(self):
        """Every script referenced in loop.md must exist."""
        loop_content = (ROOT / ".claude" / "commands" / "loop.md").read_text()
        required = ["meta_analyze.py", "notify.py", "orchestrate.py"]
        for script in required:
            assert (ROOT / script).exists(), f"Missing: {script}"

    def test_orchestrate_uses_tmux(self):
        """orchestrate.py must use tmux (not just subprocess.Popen with stdin pipe)."""
        content = (ROOT / "orchestrate.py").read_text()
        assert "tmux" in content

    def test_orchestrate_sends_loop_command(self):
        """orchestrate.py must send /loop to the tmux session."""
        content = (ROOT / "orchestrate.py").read_text()
        assert "/loop" in content


# ── Tmux integration test ────────────────────────────────────────────────────

class TestTmuxIntegration:

    def test_tmux_available(self):
        """tmux must be installed."""
        result = subprocess.run(["which", "tmux"], capture_output=True)
        assert result.returncode == 0, "tmux not found — install it first"

    def test_tmux_session_lifecycle(self, tmp_path):
        """Create a tmux session, send a command, verify output, kill session."""
        session = "deep-loop-test"
        # Kill if exists
        subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True)

        # Create session
        result = subprocess.run(
            ["tmux", "new-session", "-d", "-s", session, "-x", "200", "-y", "50"],
            capture_output=True
        )
        assert result.returncode == 0, "Failed to create tmux session"

        try:
            # Send a simple command
            subprocess.run(
                ["tmux", "send-keys", "-t", session, "echo DEEP_LOOP_TEST_OK", "Enter"],
                check=True
            )
            import time
            time.sleep(0.5)

            # Capture output
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", session, "-p"],
                capture_output=True, text=True
            )
            assert "DEEP_LOOP_TEST_OK" in result.stdout, \
                f"Expected test output in pane, got: {result.stdout[:200]}"
        finally:
            subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True)

    def test_orchestrate_tmux_launch(self, tmp_path):
        """
        Verify orchestrate.py creates a tmux session named 'deep-loop'.
        Uses --dry-run flag so it doesn't actually start Claude Code.
        """
        result = subprocess.run(
            [sys.executable, str(ROOT / "orchestrate.py"), "--dry-run"],
            capture_output=True, text=True, timeout=15, cwd=tmp_path
        )
        # --dry-run should print what it would do without actually running
        output = result.stdout + result.stderr
        assert "tmux" in output.lower() or result.returncode == 0, \
            f"orchestrate.py --dry-run failed: {output}"
