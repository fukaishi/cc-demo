import pytest
from fastapi.testclient import TestClient

from main import app
from shiritori import api
from shiritori.db import connect
from shiritori.kana import last_kana
from shiritori.routes import load_routes
from shiritori.service import ShiritoriService
from shiritori.validate import validate

FIRST_ANSWER = ["りんご", "ゴリラ", "ラッパ", "パンダ", "だるま"]


@pytest.fixture
def service():
    return ShiritoriService(connect(":memory:"), load_routes())


@pytest.fixture
def client(service):
    app.dependency_overrides[api.get_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def play(client, player_id, choices):
    state = client.post("/shiritori/plays", json={"player_id": player_id}).json()
    for step, choice in enumerate(choices, start=1):
        res = client.post(f"/shiritori/plays/{state['play_id']}/answers", json={"step": step, "choice": choice})
        assert res.status_code == 200, res.json()
        state = res.json()
    return state


@pytest.mark.parametrize(
    ("word", "kana"),
    [("りんご", "ご"), ("ゴリラ", "ら"), ("パトカー", "あ"), ("スキー", "い"), ("ダチョウ", "う"), ("リュック", "く"), ("パジャマ", "ま")],
)
def test_last_kana(word, kana):
    assert last_kana(word) == kana


def test_routes_are_valid():
    assert validate(load_routes()) == []


def test_first_answer_is_playable(client):
    state = play(client, "p1", FIRST_ANSWER)
    assert state["finished"]
    assert state["history"] == ["しりとり", *FIRST_ANSWER]
    assert state["choices"] == []


def test_play_progress(client):
    state = client.post("/shiritori/plays", json={"player_id": "p1"}).json()
    assert state["word"] == "しりとり"
    assert state["kana"] == "り"
    assert "りんご" in state["choices"]
    assert len(state["choices"]) == 4


def test_rejects_invalid_answers(client):
    play_id = client.post("/shiritori/plays", json={"player_id": "p1"}).json()["play_id"]
    url = f"/shiritori/plays/{play_id}/answers"
    assert client.post(url, json={"step": 1, "choice": "ゴリラ"}).status_code == 409
    assert client.post(url, json={"step": 2, "choice": "りんご"}).status_code == 409
    assert client.post("/shiritori/plays/nope/answers", json={"step": 1, "choice": "りんご"}).status_code == 404

    finished = play(client, "p2", FIRST_ANSWER)
    res = client.post(f"/shiritori/plays/{finished['play_id']}/answers", json={"step": 6, "choice": "マスク"})
    assert res.status_code == 409


def test_result_counts(client):
    play(client, "a", FIRST_ANSWER)
    play(client, "b", ["りんご", "ごま", "マスク", "くじら", "ラッパ"])
    me = play(client, "c", ["りんご", "ゴリラ", "らくだ", "だるま", "まくら"])

    result = client.get(f"/shiritori/plays/{me['play_id']}/result").json()
    first, second = result["steps"][0], result["steps"][1]
    assert first["counts"] == {"りんご": 3, "りす": 0, "リュック": 0, "リコーダー": 0}
    assert first["rate"] == 100 and first["is_top"]
    assert second["counts"] == {"ゴリラ": 2, "ごま": 1, "ごぼう": 0, "ごみばこ": 0}
    assert second["rate"] == 67 and second["is_top"]
    assert result["finished"]
    assert result["hits"] == 5


def test_same_player_counts_once(client):
    play(client, "a", FIRST_ANSWER)
    again = play(client, "a", ["りす", "スイカ", "カメラ", "ラッパ", "パンダ"])
    first = client.get(f"/shiritori/plays/{again['play_id']}/result").json()["steps"][0]
    assert first["counts"]["りんご"] == 1
    assert first["counts"]["りす"] == 0


def test_seed_if_empty(service):
    service.seed_if_empty()
    service.seed_if_empty()
    assert service.conn.execute("SELECT COUNT(*) FROM plays").fetchone()[0] == 1
    assert service.node_counts("しりとり")["りんご"] == 1
    assert service.node_counts("パンダ")["だるま"] == 1
