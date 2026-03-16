from __future__ import annotations

import sys
from pathlib import Path

from claudeclockwork.core.models.skill_manifest import SkillManifest
from claudeclockwork.core.registry.discovery import discover_manifest_paths
from claudeclockwork.core.registry.loader import SkillLoader


class SkillRegistry:
    def __init__(
        self,
        project_root: str | Path,
        skills_roots: list[str | Path] | tuple[str | Path, ...] | None = None,
        strict: bool = False,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.strict = strict
        configured_roots = list(skills_roots or [".claude/skills", "skills"])
        self.skills_roots = [
            (self.project_root / root).resolve() if not Path(root).is_absolute() else Path(root).resolve()
            for root in configured_roots
        ]
        self._manifests: dict[str, SkillManifest] = {}
        self._classes: dict[str, type] = {}
        self.validation_errors: list[dict] = []
        self._ensure_import_paths()

    def _ensure_import_paths(self) -> None:
        for candidate in (self.project_root, self.project_root / ".claude"):
            candidate_str = str(candidate)
            if candidate.exists() and candidate_str not in sys.path:
                sys.path.insert(0, candidate_str)

    def _validate_manifest_basic(self, manifest: SkillManifest, manifest_path: Path) -> list[dict]:
        """Return a list of validation error dicts for a manifest. Empty list = valid."""
        errors: list[dict] = []
        for field in ("name", "version", "category", "description", "entrypoint"):
            if not getattr(manifest, field, None):
                errors.append({"skill": manifest.name, "field": field, "detail": f"missing or empty: {field}"})
        return errors

    def rebuild(self) -> None:
        self._manifests.clear()
        self._classes.clear()
        self.validation_errors.clear()
        for manifest_path in discover_manifest_paths(self.skills_roots):
            manifest = SkillLoader.load_manifest(manifest_path)
            manifest.metadata.setdefault("manifest_path", str(manifest_path.relative_to(self.project_root)))
            source_root = next((root for root in self.skills_roots if root in manifest_path.parents), None)
            if source_root is not None:
                manifest.metadata.setdefault("source_root", str(source_root.relative_to(self.project_root)))

            errors = self._validate_manifest_basic(manifest, manifest_path)
            if errors:
                self.validation_errors.extend(errors)
                if self.strict:
                    import warnings as _warnings
                    _warnings.warn(
                        f"Strict mode: rejecting invalid manifest {manifest.name!r}: {errors}",
                        stacklevel=2,
                    )
                    continue
                else:
                    import sys as _sys
                    print(f"[manifest_registry] WARNING: {manifest.name} has validation issues: {errors}", file=_sys.stderr)

            self._manifests[manifest.name] = manifest
            self._classes[manifest.name] = SkillLoader.load_skill_class(manifest.entrypoint)

    def list_skills(self, enabled_only: bool = True) -> list[SkillManifest]:
        manifests = list(self._manifests.values())
        if enabled_only:
            manifests = [item for item in manifests if item.enabled]
        return sorted(manifests, key=lambda item: (item.category, item.name))

    def get_manifest(self, name: str) -> SkillManifest | None:
        return self._manifests.get(name)

    def create(self, name: str):
        cls = self._classes.get(name)
        if cls is None:
            raise KeyError(f"Unknown skill: {name}")
        return cls()

    def search(self, text: str, enabled_only: bool = True) -> list[SkillManifest]:
        needle = text.lower().strip()
        manifests = self.list_skills(enabled_only=enabled_only)
        results: list[tuple[int, SkillManifest]] = []
        tokens = set(needle.replace("_", " ").split())
        for manifest in manifests:
            corpus = " ".join([
                manifest.name,
                manifest.description,
                manifest.category,
                *manifest.aliases,
                *manifest.tags,
            ]).lower()
            score = sum(1 for token in tokens if token and token in corpus)
            if needle and needle in corpus:
                score += 3
            if score > 0:
                results.append((score, manifest))
        results.sort(key=lambda item: (-item[0], item[1].name))
        return [manifest for _, manifest in results]
