"""Unit tests for the assistant's prompt/sanitising helpers (no Gemini calls)."""

from app.services.voice_assist_service import (
    keyword_fallback,
    parse_model_json,
    sanitize_result,
)

MENU_IDS = ["vets", "diet", "buy"]
MENU = [
    {"id": "vets", "label": "Vet Doctors / पशु डॉक्टर"},
    {"id": "diet", "label": "Diet Plan / डाइट प्लान"},
    {"id": "buy", "label": "Buy Animals / पशु ख़रीदें"},
]


def test_parse_model_json_handles_fences():
    assert parse_model_json('```json\n{"intent": "answer"}\n```') == {"intent": "answer"}
    assert parse_model_json("no json here") == {}


def test_navigate_confident_auto_opens_and_drops_unknown_ids():
    r = sanitize_result(
        {"intent": "navigate", "confidence": 0.95, "matches": [{"id": "hack", "score": 1}, {"id": "vets", "score": 0.9}]},
        MENU_IDS,
        "hi",
    )
    assert r["intent"] == "navigate"
    assert r["auto_open"] is True
    assert r["matches"] == [{"id": "vets", "score": 0.9}]


def test_low_confidence_does_not_auto_open():
    r = sanitize_result({"intent": "navigate", "confidence": 0.6, "matches": [{"id": "diet", "score": 0.6}]}, MENU_IDS, "en")
    assert r["auto_open"] is False


def test_navigate_without_known_target_becomes_clarify():
    r = sanitize_result({"intent": "navigate", "confidence": 1, "matches": [{"id": "admin/delete-all"}]}, MENU_IDS, "en")
    assert r["intent"] == "clarify"
    assert r["auto_open"] is False


def test_create_proposal_is_whitelisted():
    r = sanitize_result(
        {
            "intent": "create",
            "proposal": {
                "entity": "livestock",
                "fields": {"species": "buffalo", "breed": "Murrah", "farmer_id": 999, "is_admin": True, "quantity": ""},
                "summary": "1 Murrah buffalo",
            },
        },
        MENU_IDS,
        "hi",
    )
    assert r["intent"] == "create"
    assert r["proposal"]["fields"] == {"species": "buffalo", "breed": "Murrah"}


def test_create_unknown_entity_becomes_clarify():
    r = sanitize_result({"intent": "create", "proposal": {"entity": "user", "fields": {"role": "admin"}}}, MENU_IDS, "en")
    assert r["intent"] == "clarify"
    assert r["proposal"] is None


def test_keyword_fallback_matches_labels():
    r = keyword_fallback("diet plan", MENU, "en")
    assert r["matches"][0]["id"] == "diet"
    assert r["auto_open"] is False


def test_health_record_livestock_id_must_be_own_animal():
    raw = {
        "intent": "create",
        "proposal": {"entity": "livestock_health_record", "fields": {"livestock_id": "7", "record_type": "treatment"}},
    }
    own = sanitize_result(raw, MENU_IDS, "hi", animal_ids=[7, 8])
    assert own["proposal"]["fields"]["livestock_id"] == 7
    other = sanitize_result(raw, MENU_IDS, "hi", animal_ids=[8])
    assert "livestock_id" not in other["proposal"]["fields"]


def test_clarify_keeps_only_own_animal_options_and_flags_vet_help():
    r = sanitize_result(
        {"intent": "clarify", "animal_options": [7, "8", 99, "x"], "matches": [{"id": "vets", "score": 0.7}]},
        MENU_IDS,
        "hi",
        animal_ids=[7, 8],
    )
    assert r["animal_options"] == [7, 8]
    assert r["vet_help"] is True


def test_prompt_lists_animals_and_history():
    from app.services.voice_assist_service import build_prompt

    p = build_prompt(
        MENU, "hi", "2026-09-27", "meri bhains bimar hai",
        animals=[{"id": 7, "label": "Lakshmi — Murrah buffalo"}],
        history=[{"role": "user", "text": "namaste"}],
        focus_animal_id=7,
    )
    assert "id=7: Lakshmi — Murrah buffalo" in p
    assert "user: namaste" in p
    assert "has selected this animal: id=7" in p


def test_add_livestock_task_merges_draft_and_reports_missing():
    r = sanitize_result(
        {"intent": "answer", "proposal": {"fields": {"purchase_price": 80000, "farmer_id": 5}}},
        MENU_IDS,
        "hi",
        task="add_livestock",
        draft={"species": "buffalo", "breed": "Murrah", "hack": 1},
    )
    assert r["intent"] == "create"
    assert r["proposal"]["entity"] == "livestock"
    assert r["proposal"]["fields"] == {"species": "buffalo", "breed": "Murrah", "purchase_price": 80000}
    assert r["missing"] == ["quantity", "purchase_date", "purpose"]


def test_add_livestock_correction_overrides_draft():
    r = sanitize_result(
        {"proposal": {"fields": {"breed": "Jaffarabadi"}}}, MENU_IDS, "hi", task="add_livestock", draft={"breed": "Murrah"}
    )
    assert r["proposal"]["fields"]["breed"] == "Jaffarabadi"


def test_form_prompt_includes_draft():
    from app.services.voice_assist_service import build_prompt

    p = build_prompt(MENU, "hi", "2026-09-27", "80 hazaar ki li", task="add_livestock", draft={"species": "buffalo"})
    assert '"species": "buffalo"' in p
    assert "REQUIRED: species, breed" in p
