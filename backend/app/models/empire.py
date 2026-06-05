from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base


class EmpireState(Base):
    __tablename__ = "empire_state"

    id = Column(Integer, primary_key=True, default=1)
    name = Column(String(64), default="银河帝国")
    game_date = Column(String(16), default="2252.06.05")

    # —— 资源库存 ——
    energy_credits = Column(Float, default=2847)
    minerals = Column(Float, default=1203)
    food = Column(Float, default=456)
    consumer_goods = Column(Float, default=312)
    alloys = Column(Float, default=89)
    influence = Column(Float, default=340)
    unity = Column(Float, default=1050)

    # —— 经济 ——
    energy_income = Column(Float, default=72)
    energy_expense = Column(Float, default=48)
    mineral_income = Column(Float, default=35)
    trade_value = Column(Float, default=156)
    unity_per_month = Column(Float, default=0)
    influence_per_month = Column(Float, default=0)

    # —— 军事 ——
    naval_capacity = Column(Integer, default=40)
    naval_usage = Column(Integer, default=28)
    fleet_power = Column(Integer, default=3200)
    starbase_count = Column(Integer, default=4)
    army_count = Column(Integer, default=5)
    total_ships = Column(Integer, default=0)
    military_power = Column(Integer, default=0)

    # —— 科研 ——
    physics_research = Column(Float, default=96)
    society_research = Column(Float, default=88)
    engineering_research = Column(Float, default=102)
    current_tech = Column(String(64), default="先进激光武器")
    tech_progress = Column(Float, default=65)
    researched_techs = Column(Integer, default=0)

    # —— 外交 ——
    federation_status = Column(String(32), default="理事会成员")
    border_tension = Column(String(32), default="升高")
    war_status = Column(String(32), default="和平")
    rival_count = Column(Integer, default=0)
    subject_count = Column(Integer, default=0)

    # —— 内政 ——
    population = Column(Integer, default=48)
    stability = Column(Float, default=78)
    empire_sprawl = Column(Float, default=62)
    sprawl_cap = Column(Float, default=80)
    empire_size = Column(Integer, default=0)
    planet_count = Column(Integer, default=0)
    species_count = Column(Integer, default=0)

    # —— 存档元数据 ——
    planets_summary = Column(Text, default="")
    neighbors_json = Column(Text, default="[]")
    last_save_path = Column(String(512), default="")
    last_save_time = Column(String(32), default="")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SaveData(Base):
    """存档解析的完整结构化数据（JSON 列，灵活适配版本变化）。"""
    __tablename__ = "save_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    save_name = Column(String(256))
    game_date = Column(String(16))
    empire_name = Column(String(128))
    parsed_at = Column(DateTime, server_default=func.now())

    planets_json = Column(Text, default="[]")
    fleets_json = Column(Text, default="[]")
    techs_json = Column(Text, default="[]")
    diplomacy_json = Column(Text, default="{}")
    leaders_json = Column(Text, default="[]")
    empire_json = Column(Text, default="{}")

    def to_dict(self):
        return {
            "id": self.id,
            "save_name": self.save_name,
            "game_date": self.game_date,
            "empire_name": self.empire_name,
            "parsed_at": str(self.parsed_at) if self.parsed_at else "",
        }
