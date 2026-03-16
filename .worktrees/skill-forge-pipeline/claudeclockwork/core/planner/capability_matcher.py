from __future__ import annotations

from claudeclockwork.core.models.skill_manifest import SkillManifest


class CapabilityMatcher:
    @staticmethod
    def rank(user_input: str, manifests: list[SkillManifest]) -> list[SkillManifest]:
        tokens = set(user_input.lower().replace("_", " ").split())
        scored: list[tuple[int, SkillManifest]] = []
        for manifest in manifests:
            corpus = [manifest.name, manifest.description, manifest.category, *manifest.tags, *manifest.aliases]
            score = 0
            for chunk in corpus:
                words = set(chunk.lower().replace("_", " ").split())
                score += len(tokens & words)
            if score > 0:
                scored.append((score, manifest))
        scored.sort(key=lambda item: (-item[0], item[1].name))
        return [manifest for _, manifest in scored]
