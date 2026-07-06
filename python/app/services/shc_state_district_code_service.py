from __future__ import annotations

from app.orm.shc_state_district_code import ShcStateDistrictCode


class ShcStateDistrictCodeService:
    def __init__(self) -> None:
        self.model = ShcStateDistrictCode
        self.table = "shc_state_district_codes"

    def all(self):
        return self.model().get()

    def find(self, item_id: int):
        return self.model().where('id', item_id).first()

    def where(self, filters: dict):
        query = self.model()
        for key, value in filters.items():
            query = query.where(key, value)
        return query.get()

    def create(self, data: dict):
        return self.model().create(data)

    def update(self, item_id: int, data: dict):
        record = self.model().where('id', item_id).first()
        if not record:
            return None
        for key, value in data.items():
            setattr(record, key, value)
        record.save()
        return record

    def upsert(self, data: dict):
        if 'id' in data and data['id']:
            return self.update(data['id'], data)
        return self.create(data)

    def delete(self, item_id: int) -> bool:
        record = self.model().where('id', item_id).first()
        if not record:
            return False
        record.delete()
        return True


# Singleton instance
_service = ShcStateDistrictCodeService()


# Generic getter (for auto-generated routers)
def get_service() -> ShcStateDistrictCodeService:
    """Get service instance (generic name for auto-generated code)"""
    return _service


# Specific getter (for manual/custom code compatibility)
def get_shc_state_district_code_service() -> ShcStateDistrictCodeService:
    """Get service instance (specific name for backward compatibility)"""
    return _service
