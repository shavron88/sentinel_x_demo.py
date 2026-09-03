import os
import time
import logging
import threading
from typing import Dict, List, Optional, Set

from camera.video_perspective import VideoPerspectiveValidator

logger = logging.getLogger("SentinelX.VideoEvidenceWatcher")

VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v')


class EvidenceVideoWatcher:
    """Watches the evidence/videos directory for newly added video files.

    Scans the directory periodically and exposes newly detected files so the
    camera manager can register them as live camera feeds. Once registered,
    files are remembered and not re-announced on subsequent scans.
    """

    def __init__(
        self,
        watch_dir: str = "evidence/videos",
        poll_interval: float = 5.0,
        validator: Optional[VideoPerspectiveValidator] = None,
        strict: bool = False,
    ):
        self.watch_dir = watch_dir
        self.poll_interval = poll_interval
        self.validator = validator or VideoPerspectiveValidator()
        self.strict = strict
        self._known_files: Set[str] = set()
        self._invalid_files: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callbacks = []

        os.makedirs(self.watch_dir, exist_ok=True)

    def register_callback(self, callback):
        """Register a callable that will be called for each new video file."""
        self._callbacks.append(callback)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info(f"Video evidence watcher started on: {self.watch_dir}")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _scan_new_files(self) -> List[str]:
        new_files = []
        try:
            for filename in os.listdir(self.watch_dir):
                if not filename.lower().endswith(VIDEO_EXTENSIONS):
                    continue
                full_path = os.path.join(self.watch_dir, filename)
                if os.path.isfile(full_path):
                    normalized = os.path.normpath(full_path)
                    with self._lock:
                        if normalized in self._known_files or normalized in self._invalid_files:
                            continue
                    new_files.append(normalized)
        except Exception as e:
            logger.error(f"Video evidence scan failed: {e}")
        return new_files

    def _validate_and_notify(self, filepath: str):
        if self.validator is None:
            return True

        is_valid, meta = self.validator.validate(filepath)
        if is_valid:
            with self._lock:
                self._known_files.add(filepath)
            logger.info(f"[VideoEvidence] Valid camera-perspective video detected: {filepath} | meta={meta}")
            for cb in list(self._callbacks):
                try:
                    cb(filepath)
                except Exception as e:
                    logger.error(f"Video evidence callback error: {e}")
            return True
        else:
            with self._lock:
                self._invalid_files[filepath] = meta
            logger.warning(f"[VideoEvidence] Rejected non-camera-perspective video: {filepath} | reasons={meta.get('reasons')}")
            return False

    def _watch_loop(self):
        while not self._stop_event.is_set():
            try:
                new_files = self._scan_new_files()
                for filepath in new_files:
                    self._validate_and_notify(filepath)
            except Exception as e:
                logger.error(f"Video evidence watcher loop error: {e}")

            wait = 0.5
            while wait < self.poll_interval and not self._stop_event.is_set():
                time.sleep(0.5)
                wait += 0.5

    def get_known_files(self) -> List[str]:
        with self._lock:
            return list(self._known_files)

    def get_invalid_files(self) -> Dict[str, dict]:
        with self._lock:
            return dict(self._invalid_files)

    def initial_scan(self) -> List[str]:
        """Perform an initial scan of existing files and register valid ones."""
        registered = []
        for filename in os.listdir(self.watch_dir):
            if not filename.lower().endswith(VIDEO_EXTENSIONS):
                continue
            full_path = os.path.join(self.watch_dir, filename)
            if os.path.isfile(full_path):
                normalized = os.path.normpath(full_path)
                with self._lock:
                    if normalized in self._known_files or normalized in self._invalid_files:
                        continue
                if self._validate_and_notify(normalized):
                    registered.append(normalized)
        return registered
