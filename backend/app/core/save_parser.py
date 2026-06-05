"""
Stellaris 存档解析器 v2。

基于 ClausewitzTokenizer 的流式解析，从前 500KB regex 升级为完整的结构化提取。
提取: 帝国数据 / 星球 / 舰队 / 科技 / 外交 / 领袖

存档结构:
  .sav = zip 文件
    ├── meta       — 游戏版本、日期等元数据
    └── gamestate  — 完整游戏状态 (Clausewitz 文本, 通常 50-200MB+)
"""

import zipfile
from io import BytesIO
from dataclasses import dataclass, field
from typing import Any

from .clausewitz_tokenizer import ClausewitzTokenizer


@dataclass
class ParsedPlanet:
    name: str = ""
    planet_class: str = ""
    designation: str = ""
    population: int = 0
    stability: float = 0
    districts: dict = field(default_factory=dict)
    buildings: list[str] = field(default_factory=list)


@dataclass
class ParsedFleet:
    name: str = ""
    fleet_power: int = 0
    ship_count: int = 0
    location: str = ""


@dataclass
class ParsedLeader:
    name: str = ""
    leader_class: str = ""
    level: int = 0
    traits: list[str] = field(default_factory=list)


def parse_save(file_data: bytes) -> dict:
    """解析 Stellaris 存档文件。保持向后兼容的返回格式。"""
    result = {
        "meta": {},
        "empire": {},
        "resources": {},
        "planets": [],
        "fleets": [],
        "technologies": [],
        "diplomacy": {},
        "leaders": [],
        "neighbors": [],
        "parsed": False,
        "error": None,
    }

    try:
        with zipfile.ZipFile(BytesIO(file_data)) as zf:
            file_list = zf.namelist()

            if "meta" in file_list:
                meta_text = zf.read("meta").decode("utf-8", errors="replace")
                result["meta"] = _parse_meta(meta_text)

            if "gamestate" in file_list:
                gs_bytes = zf.read("gamestate")
                gs_text = gs_bytes.decode("utf-8", errors="replace")
                _extract_gamestate(gs_text, result)

            result["parsed"] = True
    except zipfile.BadZipFile:
        result["error"] = "无效的存档文件（非 zip 格式）"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"

    return result


# ═══════════════════════════════════════════════════════════
# 内部实现
# ═══════════════════════════════════════════════════════════



def _parse_meta(text: str) -> dict:
    """解析 meta 文件中的简单 key=value 行。"""
    data = {}
    t = ClausewitzTokenizer(text)
    while not t.at_end():
        t.skip_blank()
        if t.at_end():
            break
        key = t.read_bare_word()
        t.skip_blank()
        if t.peek() == "=":
            t.advance()
            t.skip_blank()
            data[key] = t.parse_value()
    return data


def _extract_gamestate(gs_text: str, result: dict):
    """从 gamestate 文本中提取所有需要的数据。"""
    t = ClausewitzTokenizer(gs_text)
    player_country_idx = "0"  # 默认

    # 第一遍：找到 player country index（player 块在文件开头附近）
    while not t.at_end():
        t.skip_blank()
        if t.at_end():
            break
        key = t.read_bare_word()
        t.skip_blank()
        if t.peek() == "=":
            t.advance()
            t.skip_blank()

        if key == "player" and t.peek() == "{":
            player_data = t.parse_value()
            if isinstance(player_data, dict):
                for v in player_data.values():
                    if isinstance(v, dict) and "country" in v:
                        player_country_idx = str(v["country"])
                        break
            break  # player 块已找到
        elif t.peek() == "{":
            t.skip_block()
        else:
            t.parse_value()

    # 第二遍：完整扫描所有数据
    t = ClausewitzTokenizer(gs_text)
    while not t.at_end():
        t.skip_blank()
        if t.at_end():
            break

        key = t.read_bare_word()
        t.skip_blank()
        if t.peek() == "=":
            t.advance()
            t.skip_blank()

        if key == "date":
            result["empire"]["date"] = t.parse_value()

        elif key == "country":
            if t.peek() == "{":
                _, cdata, all_empires = _extract_player_country(t, player_country_idx)
                if cdata:
                    result["empire"].update(_parse_country_data(cdata))
                    result["neighbors"] = all_empires
            else:
                _skip_value(t)

        elif key == "planets":
            _extract_planets(t, result, player_country_idx)

        elif key == "fleet":
            _extract_fleets_v2(t, result, player_country_idx)

        elif key == "war":
            war_data = t.parse_value()
            result.setdefault("diplomacy", {})["wars"] = _summarize_wars(war_data)

        elif key == "technology":
            _extract_technology(t, result)

        elif key == "species":
            result["empire"]["species_count"] = _count_block_entries(t)

        elif key == "leaders":
            _extract_leaders(t, result)

        else:
            _skip_value(t)


def _extract_player_country(t: ClausewitzTokenizer, player_idx: str):
    """从 country={...} 块中提取玩家国家数据和所有帝国摘要。返回 (owned_planet_ids, country_data, all_empires)。"""
    if t.peek() != "{":
        _skip_value(t)
        return set(), None, []

    t.advance()
    owned: set[str] = set()
    country_data = None
    all_empires: list[dict] = []

    while not t.at_end():
        t.skip_blank()
        if t.at_end() or t.peek() == "}":
            break

        idx_key = t.read_bare_word()
        t.skip_blank()
        if t.peek() == "=":
            t.advance()
            t.skip_blank()

        if t.peek() == "{":
            data = t.parse_value()
            if isinstance(data, dict):
                name = _extract_string(data.get("name", ""))
                mp = _to_number(data.get("military_power", 0))
                ep = _to_number(data.get("economy_power", 0))
                tp = _to_number(data.get("tech_power", 0))
                fs = int(_to_number(data.get("fleet_size", 0)))
                gov = data.get("government", {})
                gtype = gov.get("type", "") if isinstance(gov, dict) else ""
                personality = data.get("personality", "")
                flag = data.get("flag", {})

                if idx_key == player_idx:
                    country_data = data
                    op = data.get("owned_planets", {})
                    if isinstance(op, dict):
                        for pid in op:
                            owned.add(str(pid))
                elif name and float(mp) > 0:
                    # 排除无名字或军力为0的条目（通常是死国家/特殊实体）
                    all_empires.append({
                        "id": idx_key,
                        "name": name,
                        "military_power": mp,
                        "economy_power": ep,
                        "tech_power": tp,
                        "fleet_size": fs,
                        "government": gtype,
                        "personality": personality,
                    })
        else:
            _skip_value(t)

    t.skip_blank()
    if t.peek() == "}":
        t.advance()

    # 按军力降序排列
    all_empires.sort(key=lambda x: x["military_power"], reverse=True)
    return owned, country_data, all_empires


def _extract_planets(t: ClausewitzTokenizer, result: dict, player_idx: str):
    """提取殖民星球数据。planets={planet={0={...} 1={...} ...}} 按 controller 过滤。"""
    if t.peek() != "{":
        _skip_value(t)
        return

    t.advance()
    planets = []

    while not t.at_end():
        t.skip_blank()
        if t.at_end() or t.peek() == "}":
            break

        key = t.read_bare_word()
        t.skip_blank()
        if t.peek() == "=":
            t.advance()
            t.skip_blank()

        if key == "planet" and t.peek() == "{":
            t.advance()
            while not t.at_end():
                t.skip_blank()
                if t.at_end() or t.peek() == "}":
                    break

                t.read_bare_word()  # planet_id
                t.skip_blank()
                if t.peek() == "=":
                    t.advance()
                    t.skip_blank()

                if t.peek() == "{":
                    planet_data = t.parse_value()
                    # 按 controller 字段过滤（匹配玩家国家）
                    ctrl = str(planet_data.get("controller", "")) if isinstance(planet_data, dict) else ""
                    if ctrl == player_idx:
                        planet = _parse_planet(planet_data)
                        if planet and planet.population > 0:
                            planets.append(planet)
                else:
                    _skip_value(t)

            t.skip_blank()
            if t.peek() == "}":
                t.advance()
        else:
            _skip_value(t)

    result["planets"] = planets
    result["empire"]["planet_count"] = len(planets)
    result["empire"]["planets_summary"] = _format_planet_summary(planets)

    if planets:
        result["empire"]["population"] = sum(p.population for p in planets)
        result["empire"]["stability"] = round(
            sum(p.stability * p.population for p in planets) / result["empire"]["population"], 1
        )

    t.skip_blank()
    if t.peek() == "}":
        t.advance()


def _extract_fleets_v2(t: ClausewitzTokenizer, result: dict, player_idx: str):
    """提取玩家舰队数据。fleet={id={...owner=player_idx...}}"""
    if t.peek() != "{":
        _skip_value(t)
        return

    t.advance()
    fleets = []
    total_power = 0
    total_ships = 0

    while not t.at_end():
        t.skip_blank()
        if t.at_end() or t.peek() == "}":
            break

        fleet_id = t.read_bare_word()
        t.skip_blank()
        if t.peek() == "=":
            t.advance()
            t.skip_blank()

        if t.peek() == "{":
            fleet_data = t.parse_value()
            # 只统计属于玩家的舰队
            owner = str(fleet_data.get("owner", "")) if isinstance(fleet_data, dict) else ""
            if owner == player_idx:
                fleet = _parse_fleet(fleet_data)
                if fleet and fleet.ship_count > 0:
                    fleets.append(fleet)
                    total_power += fleet.fleet_power
                    total_ships += fleet.ship_count
        else:
            _skip_value(t)

    result["fleets"] = fleets
    result["empire"]["total_ships"] = result["empire"].get("total_ships", 0) or total_ships
    result["empire"]["fleet_power"] = result["empire"].get("fleet_power", 0) or total_power

    t.skip_blank()
    if t.peek() == "}":
        t.advance()


def _extract_technology(t: ClausewitzTokenizer, result: dict):
    """提取科技状态。"""
    if t.peek() != "{":
        _skip_value(t)
        return

    techs = t.parse_value()
    # 统计已研究科技
    researched = []
    for k, v in techs.items():
        if isinstance(v, dict):
            level = v.get("level", 0)
            if isinstance(level, (int, float)) and level > 0:
                researched.append(k)
        elif isinstance(v, (int, float)) and v > 0:
            researched.append(k)

    result["technologies"] = researched
    result["empire"]["researched_techs"] = len(researched)

    # 尝试找当前研究
    for k, v in techs.items():
        if isinstance(v, dict) and v.get("progress"):
            if isinstance(v.get("level", 0), (int, float)) and v["level"] == 0:
                result["empire"]["current_tech"] = k
                result["empire"]["tech_progress"] = _to_number(v.get("progress", 0))


def _extract_leaders(t: ClausewitzTokenizer, result: dict):
    """提取领袖数据。"""
    if t.peek() != "{":
        _skip_value(t)
        return
    leaders_data = t.parse_value()
    if isinstance(leaders_data, dict):
        result["leaders"] = [
            parsed for v in leaders_data.values()
            if (parsed := _parse_leader(v)) is not None
        ]


def _summarize_wars(war_data: dict) -> dict:
    """摘要战争状态。"""
    return {
        "active_count": len(war_data) if isinstance(war_data, dict) else 0,
    }


# ═══════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════

def _skip_value(t: ClausewitzTokenizer):
    """跳过当前位置的值（不解析）。"""
    ch = t.peek()
    if ch == '"':
        t.read_quoted_string()
    elif ch == "{":
        t.skip_block()
    elif ch == "@":
        t.advance()
        t.read_bare_word()
    else:
        t.read_bare_word()


def _count_block_entries(t: ClausewitzTokenizer) -> int:
    """计算 '{...}' 中顶层条目的数量。"""
    if t.peek() != "{":
        _skip_value(t)
        return 0
    t.advance()
    count = 0
    while not t.at_end():
        t.skip_blank()
        if t.at_end() or t.peek() == "}":
            break
        t.read_bare_word()
        t.skip_blank()
        if t.peek() == "=":
            t.advance()
            t.skip_blank()
        _skip_value(t)
        count += 1
    t.skip_blank()
    if t.peek() == "}":
        t.advance()
    return count


def _extract_string(val: Any) -> str:
    """从值中提取字符串。处理本地化引用 {key=..., literal=yes} 格式。"""
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return str(val.get("key", val.get("name", "")))
    return str(val) if val else ""


def _to_number(val: Any) -> float:
    """安全转换为数字。"""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val)
        except ValueError:
            return 0.0
    return 0.0


# ═══════════════════════════════════════════════════════════
# 数据项解析
# ═══════════════════════════════════════════════════════════

def _parse_country_data(data: dict) -> dict:
    """从国家数据 dict 中提取帝国关键指标（基于实际存档字段名）。"""
    result = {}

    if "name" in data:
        result["name"] = _extract_string(data["name"])

    # 预算中的收入（country_base）
    budget = data.get("budget", {})
    if isinstance(budget, dict):
        current = budget.get("current_month", budget)
        income = current.get("income", current) if isinstance(current, dict) else {}
        cb = income.get("country_base", income) if isinstance(income, dict) else {}

        resource_map = {
            "energy": "energy_credits", "minerals": "minerals", "food": "food",
            "consumer_goods": "consumer_goods", "alloys": "alloys",
            "influence": "influence", "unity": "unity",
            "physics_research": "physics_research",
            "society_research": "society_research",
            "engineering_research": "engineering_research",
        }
        for rk, label in resource_map.items():
            val = _deep_get(cb, income, rk)
            if val is not None:
                result[label] = _to_number(val)

        # 收入/支出
        for rk, label in [("energy", "energy_income"), ("minerals", "mineral_income")]:
            val = _deep_get(income, None, rk)
            if val is not None:
                result[label] = _to_number(val)

    # 舰队
    result["fleet_power"] = _to_number(data.get("military_power", 0))
    result["naval_usage"] = int(_to_number(data.get("used_naval_capacity", 0)))
    result["total_ships"] = int(_to_number(data.get("fleet_size", 0)))
    result["starbase_capacity"] = int(_to_number(data.get("starbase_capacity", 0)))
    result["starbase_count"] = int(_to_number(data.get("num_upgraded_starbase", 0)))

    # 经济/科技评分
    result["economy_power"] = _to_number(data.get("economy_power", 0))
    result["tech_power"] = _to_number(data.get("tech_power", 0))

    # 帝国规模
    result["empire_sprawl"] = _to_number(data.get("empire_size", 0))
    result["sprawl_cap"] = 80.0

    # 当前科技
    ts = data.get("tech_status", {})
    if isinstance(ts, dict):
        cur_tech = ts.get("technology", "")
        if cur_tech:
            result["current_tech"] = cur_tech
        result["tech_progress"] = _to_number(ts.get("stored_techpoints", 0))

    # 人口
    result["population"] = int(_to_number(data.get("num_sapient_pops", 0)))
    result["employable_pops"] = int(_to_number(data.get("employable_pops", 0)))

    # 胜利分数
    result["victory_score"] = _to_number(data.get("victory_score", 0))
    result["victory_rank"] = int(_to_number(data.get("victory_rank", 0)))

    # 个性/政体
    result["personality"] = str(data.get("personality", ""))
    gov = data.get("government", {})
    if isinstance(gov, dict):
        result["government_type"] = str(gov.get("type", ""))

    return result


def _deep_get(d: dict, fallback: dict | None, key: str):
    """从 dict 或 fallback 中获取值。"""
    if isinstance(d, dict) and key in d:
        return d[key]
    if isinstance(fallback, dict) and key in fallback:
        return fallback[key]
    return None


def _parse_planet(data: dict) -> ParsedPlanet | None:
    """解析单个星球数据。"""
    if not isinstance(data, dict):
        return None

    name = _extract_string(data.get("name", "?"))
    if name == "?":
        return None

    # 人口可能在 pop, population, num_sapient_pops 字段
    pop = data.get("pop", data.get("population", data.get("num_sapient_pops", 0)))
    if isinstance(pop, dict):
        pop = sum(int(_to_number(v)) for v in pop.values() if isinstance(v, (int, float)))

    planet = ParsedPlanet(
        name=name,
        planet_class=_extract_string(data.get("planet_class", "")),
        designation=_extract_string(data.get("designation", data.get("planet_designation", ""))),
        population=int(_to_number(pop)),
        stability=round(_to_number(data.get("stability", 50)), 1),
    )

    # 区划
    districts = data.get("districts", {})
    if isinstance(districts, dict):
        planet.districts = {k: int(_to_number(v)) for k, v in districts.items()
                           if isinstance(v, (int, float, str))}

    # 建筑
    buildings = data.get("buildings", {})
    if isinstance(buildings, dict):
        planet.buildings = [str(v.get("name", v)) for v in buildings.values()
                          if isinstance(v, dict) and "name" in v]

    return planet


def _parse_fleet(data: dict) -> ParsedFleet | None:
    """解析单个舰队数据。"""
    if not isinstance(data, dict):
        return None

    name = str(data.get("name", ""))
    if not name:
        return None

    fleet = ParsedFleet(
        name=name,
        fleet_power=int(_to_number(data.get("fleet_power", 0))),
        location=str(data.get("location", data.get("system", data.get("orbit", "")))),
    )

    # 舰船数量
    ships = data.get("ships", {})
    if isinstance(ships, dict):
        fleet.ship_count = len(ships)
    elif isinstance(ships, (int, float)):
        fleet.ship_count = int(ships)

    return fleet


def _parse_leader(data: dict) -> ParsedLeader | None:
    """解析单个领袖数据。"""
    if not isinstance(data, dict):
        return None
    name = data.get("name", "")
    if not name:
        return None
    return ParsedLeader(
        name=str(name),
        leader_class=str(data.get("class", data.get("leader_class", ""))),
        level=int(_to_number(data.get("level", 0))),
        traits=[str(v) for v in data.get("traits", {}).values() if isinstance(v, str)],
    )


def _format_planet_summary(planets: list[ParsedPlanet]) -> str:
    """格式化星球一览文本，用于注入 Agent 提示。"""
    if not planets:
        return "暂无数据"

    lines = []
    for p in planets:
        desig = f" · {p.designation}" if p.designation else ""
        lines.append(
            f"{p.name} · {p.planet_class}{desig} · "
            f"人口 {p.population} · 稳定度 {p.stability}%"
        )

    # 限制 20 行避免超过 token 预算
    if len(lines) > 20:
        lines = lines[:20]
        lines.append(f"... 等共 {len(planets)} 颗星球")

    return "\n".join(lines)
