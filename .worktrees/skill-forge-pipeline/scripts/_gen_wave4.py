"""Generate Wave 4 skill wrappers — run once then delete."""
from __future__ import annotations
import json, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_BASE = ROOT / '.claude' / 'skills'

# (skill_id, category, description, permissions, tags)
SKILLS = [
    # routing
    ("bandit_router_select",        "routing",     "Select the optimal model tier using multi-armed bandit routing logic.",          ["registry:read"],             ["routing","bandit","model-selection"]),
    ("budget_router",               "routing",     "Route tasks based on token budget and cost constraints.",                         ["registry:read"],             ["routing","budget","cost"]),
    ("budget_analyze",              "routing",     "Analyse token and cost budget consumption across recent runs.",                   ["registry:read"],             ["budget","analytics","cost"]),
    ("escalation_router",           "routing",     "Route escalations to the appropriate agent tier based on severity.",              ["registry:read"],             ["routing","escalation","agents"]),
    ("model_routing_select",        "routing",     "Select the best model for a given task using the routing matrix.",                ["registry:read"],             ["routing","model-selection"]),
    ("model_routing_record_outcome","routing",     "Record the outcome of a model routing decision for future tuning.",               ["registry:write"],            ["routing","outcome","ledger"]),
    ("route_autotune_suggest",      "routing",     "Suggest routing profile adjustments based on historical outcome data.",           ["registry:read"],             ["routing","autotune","optimization"]),
    ("route_profile_update",        "routing",     "Write updated routing profile settings to the registry.",                         ["registry:write"],            ["routing","profile","config"]),
    # planning
    ("create_mvp",                  "planning",    "Scaffold a new MVP document from a goal description.",                            ["docs:write","repo:read"],    ["planning","mvp","scaffold"]),
    ("creativity_burst",            "planning",    "Generate a rapid creative ideation burst for a given problem.",                   ["repo:read"],                 ["planning","creativity","ideation"]),
    ("decision_feedback",           "planning",    "Capture structured feedback on a decision for future reference.",                 ["repo:read"],                 ["planning","decision","feedback"]),
    ("deliberation_pack_build",     "planning",    "Build a deliberation pack with options, tradeoffs, and recommendation.",          ["repo:read"],                 ["planning","deliberation","decision"]),
    ("economics_regression",        "planning",    "Run cost/value regression analysis on a set of options.",                         ["repo:read"],                 ["planning","economics","analysis"]),
    ("edge_case_selector",          "planning",    "Identify and prioritise edge cases for a given feature or change.",               ["repo:read"],                 ["planning","edge-cases","qa"]),
    ("hypothesis_builder",          "planning",    "Build a structured hypothesis from an observation and supporting evidence.",      ["repo:read"],                 ["planning","hypothesis","research"]),
    ("idea_dedupe",                 "planning",    "Deduplicate a list of ideas by semantic similarity.",                             ["repo:read"],                 ["planning","deduplication","ideas"]),
    ("idea_scoring",                "planning",    "Score and rank ideas by feasibility, impact, and alignment.",                     ["repo:read"],                 ["planning","scoring","prioritisation"]),
    ("plan_diff_apply",             "planning",    "Apply a structured diff to an existing plan document.",                           ["docs:write","repo:read"],    ["planning","diff","documents"]),
    ("plan_lint",                   "planning",    "Lint a plan document for missing sections and policy violations.",                ["repo:read"],                 ["planning","lint","qa"]),
    ("plan_mutate",                 "planning",    "Apply a targeted mutation to a plan section.",                                    ["docs:write","repo:read"],    ["planning","mutation","documents"]),
    ("triad_build",                 "planning",    "Build a message triad (work_brief, constraints, goal) from a raw task.",          ["repo:read"],                 ["planning","triad","message"]),
    ("triad_ref_lint",              "planning",    "Lint a triad for reference consistency and completeness.",                        ["repo:read"],                 ["planning","lint","triad"]),
    ("work_scope_assess",           "planning",    "Assess the scope and complexity of a proposed work item.",                        ["repo:read"],                 ["planning","scope","assessment"]),
    # analysis
    ("code_assimilate",             "analysis",    "Assimilate and summarise a code module or directory for agent context.",          ["repo:read"],                 ["analysis","code","summary"]),
    ("limitation_harvest_scan",     "analysis",    "Scan the codebase for documented limitations and known issues.",                  ["repo:read"],                 ["analysis","limitations","scan"]),
    ("mechanic_explain",            "analysis",    "Explain how a skill or system component works in plain language.",                ["repo:read"],                 ["analysis","explanation","docs"]),
    ("mutation_detect",             "analysis",    "Detect unintended mutations between two versions of a file or data structure.",   ["repo:read"],                 ["analysis","mutation","diff"]),
    ("pattern_detect",              "analysis",    "Detect recurring patterns in a set of skill outputs or log entries.",             ["repo:read"],                 ["analysis","patterns","detection"]),
    ("system_map",                  "analysis",    "Build a dependency and interaction map for the current system.",                   ["repo:read"],                 ["analysis","system-map","architecture"]),
    # docs
    ("autodocs_generate",           "docs",        "Auto-generate documentation from code, manifests, and inline comments.",          ["docs:write","repo:read"],    ["docs","generation","automation"]),
    ("copyright_standardize",       "docs",        "Standardise copyright headers across all source files.",                          ["docs:write","repo:read"],    ["docs","copyright","standardisation"]),
    ("doc_review",                  "docs",        "Review a document for completeness, accuracy, and policy compliance.",            ["repo:read"],                 ["docs","review","qa"]),
    ("doc_ssot_resolver",           "docs",        "Resolve conflicting SSoT references across documentation.",                       ["docs:write","repo:read"],    ["docs","ssot","resolver"]),
    ("doc_write",                   "docs",        "Write a new document from a structured brief.",                                   ["docs:write"],                ["docs","writing","generation"]),
    ("pdf_export",                  "docs",        "Export a markdown document to a formatted PDF file.",                             ["docs:write","repo:read"],    ["docs","pdf","export"]),
    ("screencast_script",           "docs",        "Generate a screencast narration script from a feature description.",              ["docs:write"],                ["docs","screencast","script"]),
    ("tutorial_write",              "docs",        "Write a step-by-step tutorial for a skill or workflow.",                          ["docs:write"],                ["docs","tutorial","writing"]),
    ("log_standardize",             "docs",        "Standardise log file format and line structure across the repository.",           ["docs:write","repo:read"],    ["docs","logs","standardisation"]),
    # performance
    ("token_event_log",             "performance", "Log a token-usage event to the performance ledger.",                              ["registry:write"],            ["performance","tokens","ledger"]),
    ("prompt_debt_capture",         "performance", "Capture prompt debt observations for future prompt engineering work.",            ["repo:read"],                 ["performance","prompt-debt","tracking"]),
    ("efficiency_review",           "performance", "Review token efficiency and cost metrics for a set of skill runs.",               ["repo:read"],                 ["performance","efficiency","review"]),
    ("shadow_prompt",               "performance", "Generate a shadow (minimised) prompt for a given skill or workflow.",             ["repo:read"],                 ["performance","shadow-prompt","optimisation"]),
    ("shadow_prompt_minify",        "performance", "Minify a shadow prompt to its smallest effective form.",                          ["repo:read"],                 ["performance","minification","prompt"]),
    # archive
    ("last_train",                  "archive",     "Run the last-train knowledge consolidation pass.",                                ["repo:read"],                 ["archive","knowledge","consolidation"]),
    ("last_train_merge",            "archive",     "Merge last-train output into the knowledge base.",                                ["repo:write","repo:read"],    ["archive","merge","knowledge"]),
    # misc
    ("critics_board_review",        "misc",        "Run a full critics board review for a plan or implementation.",                   ["repo:read"],                 ["misc","critics","review"]),
    ("exec_dryrun",                 "misc",        "Dry-run an execution plan without applying any changes.",                         ["repo:read"],                 ["misc","dryrun","validation"]),
    ("review_panel",                "misc",        "Convene a review panel for multi-perspective evaluation.",                        ["repo:read"],                 ["misc","review","panel"]),
    # demo
    ("report",                      "demo",        "Generate a simple status report (demo skill).",                                   ["repo:read"],                 ["demo","report"]),
    ("scan",                        "demo",        "Scan the repository for a quick health summary (demo skill).",                    ["repo:read"],                 ["demo","scan"]),
    ("hello",                       "demo",        "Hello-world demo skill.",                                                         ["repo:read"],                 ["demo","hello"]),
]


def class_name(skill_id: str) -> str:
    return ''.join(part.title() for part in skill_id.split('_')) + 'Skill'


def entrypoint(skill_id: str, category: str) -> str:
    return f"skills.{category}.{skill_id}.skill:{class_name(skill_id)}"


def main() -> None:
    # Ensure category __init__.py files exist
    for cat in set(row[1] for row in SKILLS):
        cat_dir = SKILLS_BASE / cat
        cat_dir.mkdir(parents=True, exist_ok=True)
        cat_init = cat_dir / '__init__.py'
        if not cat_init.exists():
            cat_init.write_text('', encoding='utf-8')

    created = 0
    for skill_id, category, description, permissions, tags in SKILLS:
        skill_dir = SKILLS_BASE / category / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)

        (skill_dir / '__init__.py').write_text('', encoding='utf-8')

        manifest = {
            "id": skill_id,
            "name": skill_id,
            "version": "1.0.0",
            "category": category,
            "description": description,
            "entrypoint": entrypoint(skill_id, category),
            "permissions": permissions,
            "aliases": [],
            "tags": tags,
            "enabled": True,
            "trust_level": "local",
            "inputs": {},
            "outputs": {},
            "metadata": {"legacy_bridge": skill_id},
        }
        (skill_dir / 'manifest.json').write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
        )

        cls = class_name(skill_id)
        skill_py = textwrap.dedent(f'''\
            from __future__ import annotations

            from claudeclockwork.legacy.adapter import LegacySkillAdapter


            class {cls}(LegacySkillAdapter):
                legacy_skill_id = "{skill_id}"
        ''')
        (skill_dir / 'skill.py').write_text(skill_py, encoding='utf-8')
        created += 1

    print(f'Wave 4: created {created} skill packages across '
          f'{len(set(row[1] for row in SKILLS))} categories')


if __name__ == '__main__':
    main()
