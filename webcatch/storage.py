# -*- coding: utf-8 -*-
"""
存储模块 — 快照持久化 + 变更历史 + 进程状态
"""
import os
import json
import hashlib
import datetime
import logging

logger = logging.getLogger("webcatch.storage")


class Storage:
    """统一的快照/历史/状态存储"""

    def __init__(self, config=None):
        cfg = config or {}
        self.snapshot_dir = cfg.get("snapshot_dir", "data/snapshots")
        self.history_dir = cfg.get("history_dir", "data/history")
        self.state_file = cfg.get("state_file", "data/state.json")
        os.makedirs(self.snapshot_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)

    # ---- 快照 ----

    def _snapshot_path(self, name):
        h = hashlib.md5(name.encode()).hexdigest()[:12]
        return os.path.join(self.snapshot_dir, f"{h}.txt")

    def load_snapshot(self, name):
        path = self._snapshot_path(name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def save_snapshot(self, name, content):
        path = self._snapshot_path(name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    # ---- 变更历史（JSON Lines）----

    def _history_path(self, name):
        h = hashlib.md5(name.encode()).hexdigest()[:12]
        return os.path.join(self.history_dir, f"{h}.jsonl")

    def save_history(self, name, old_content, new_content):
        path = self._history_path(name)
        record = {
            "time": datetime.datetime.now().isoformat(),
            "name": name,
            "old_len": len(old_content) if old_content else 0,
            "new_len": len(new_content) if new_content else 0,
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # ---- 进程状态 ----

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_state(self, state):
        os.makedirs(os.path.dirname(self.state_file) or ".", exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def update_check_time(self, name):
        state = self.load_state()
        state.setdefault("last_checks", {})[name] = datetime.datetime.now().isoformat()
        self.save_state(state)
