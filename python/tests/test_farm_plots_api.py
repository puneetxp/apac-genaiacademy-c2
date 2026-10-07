"""create_plot / get_farm_plots / delete_plot with the ORM mocked (no database)."""

import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1 import farms as farms_api

NOW = datetime(2026, 9, 27)


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def get(self):
        return SimpleNamespace(items=self.items)


class FakeFarmPlot:
    """Stands in for app.orm.farm_plot.FarmPlot and records what the API asks for."""

    wheres, creates, updates = [], [], []
    rows = []

    def __init__(self, items=None):
        self.items = items or {}

    @classmethod
    def where(cls, cond):
        cls.wheres.append(cond)
        rows = [r for r in cls.rows if all(r.get(k) in v for k, v in cond.items())]
        q = FakeQuery(rows)
        q.update = lambda data: cls.updates.append((cond, data))
        return q

    @classmethod
    def create(cls, data):
        cls.creates.append(data)
        row = {"id": 7, "created_at": NOW, "updated_at": NOW, **data}
        return SimpleNamespace(get_inserted=lambda: cls(row))


@pytest.fixture
def api(monkeypatch):
    FakeFarmPlot.wheres, FakeFarmPlot.creates, FakeFarmPlot.updates = [], [], []
    FakeFarmPlot.rows = [
        {"id": 1, "farm_id": 11, "plot_name": "A", "area": 2, "soil_type": "clay", "irrigation_type": "canal", "enable": 1, "created_at": NOW, "updated_at": NOW},
        {"id": 2, "farm_id": 11, "plot_name": "Old", "area": 1, "soil_type": "clay", "irrigation_type": "canal", "enable": 0, "created_at": NOW, "updated_at": NOW},
    ]
    farm = {"id": 11, "owner_id": 5, "location_state": "Gujarat", "location_district": "Anand", "primary_soil_type": "loamy"}
    monkeypatch.setattr(farms_api, "FarmPlot", FakeFarmPlot)
    monkeypatch.setattr(farms_api, "Farm", SimpleNamespace(where=lambda c: FakeQuery([farm] if 11 in c.get("id", []) else [])))
    monkeypatch.setattr(farms_api, "ActiveRole", SimpleNamespace(where=lambda c: FakeQuery([{"id": 3}])))
    return SimpleNamespace(owner=SimpleNamespace(id=5, user_type="farmer"), other=SimpleNamespace(id=6, user_type="farmer"))


def run(coro):
    return asyncio.run(coro)


def test_create_plot_uses_route_farm_id(api):
    body = farms_api.PlotCreate(name="North field", area_acres=3.5)
    res = run(farms_api.create_plot(11, body, api.owner, None))
    assert res.name == "North field" and res.farm_id == 11 and res.area_acres == 3.5
    created = FakeFarmPlot.creates[0]
    assert created["farm_id"] == 11 and created["soil_type"] == "loamy" and created["enable"] == 1


def test_create_plot_rejects_other_users_farm(api):
    with pytest.raises(HTTPException) as e:
        run(farms_api.create_plot(11, farms_api.PlotCreate(name="X", area_acres=1), api.other, None))
    assert e.value.status_code == 403


def test_plot_list_hides_deleted_plots(api):
    res = run(farms_api.get_farm_plots(11, api.owner, None))
    assert [p.name for p in res.plots] == ["A"]
    assert FakeFarmPlot.wheres[-1] == {"farm_id": [11], "enable": [1]}


def test_delete_plot_soft_deletes_with_enable(api):
    run(farms_api.delete_plot(11, 1, api.owner, None))
    assert FakeFarmPlot.updates == [({"id": [1]}, {"enable": 0})]
