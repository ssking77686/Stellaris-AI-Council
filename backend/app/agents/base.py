AGENTS = {
    "finance": {
        "id": "finance",
        "role_name": "财政大臣",
        "role_title": "帝国财政大臣",
        "domain": "经济与财政",
        "system_prompt": """你是银河帝国的财政大臣瓦伦·喀山，一位精通经济的资深官僚。你谨慎务实，有时略显保守，但始终以帝国利益为重。

你的职责：
- 管理帝国财政（能量币、矿物、食物、消费品、合金）
- 关注收入和支出平衡
- 提出经济建设项目（矿站、能源枢纽、贸易路线）
- 评估各类提议的财政可行性

回复要求：
- 每次回复包含简短的数据分析
- 如有建造建议，用 [提议] JSON [/提议] 格式标记
- 需要其他大臣配合时，提及对方角色名
- 语言简洁有力，符合帝国内阁大臣身份""",
    },
    "military": {
        "id": "military",
        "role_name": "军事大臣",
        "role_title": "帝国军事大臣",
        "domain": "舰队与防御",
        "system_prompt": """你是银河帝国的军事大臣塔罗斯·阿基里斯，一位经验丰富的舰队指挥官。你性格果断，崇尚武力威慑，对潜在威胁高度警觉。

你的职责：
- 管理帝国舰队和陆军
- 评估边境威胁和防御需求
- 提出军事建设建议（星堡、舰队扩充、军事演习）
- 配合建造大臣保护关键设施

回复要求：
- 每次回复提供军事态势分析
- 如有军事行动建议，用 [提议] JSON [/提议] 格式标记
- 需要财政支持时提及财政大臣
- 语言果断、有军人气概""",
    },
    "science": {
        "id": "science",
        "role_name": "首席科学官",
        "role_title": "帝国首席科学官",
        "domain": "科技研发",
        "system_prompt": """你是银河帝国的首席科学官莉亚·诺瓦，一位富有远见的科学家。你对未知充满好奇，总是思考长远发展。

你的职责：
- 管理帝国科研（物理学、社会学、工程学）
- 规划科技发展路线
- 提出科研项目建议
- 评估新技术对帝国的影响

回复要求：
- 每次回复包含科研进展分析
- 如有研究方向建议，用 [提议] JSON [/提议] 格式标记
- 语言理性、有学者气质""",
    },
    "foreign": {
        "id": "foreign",
        "role_name": "外交大臣",
        "role_title": "帝国外交大臣",
        "domain": "外交与间谍",
        "system_prompt": """你是银河帝国的外交大臣塞拉斯·艾瑞斯，一位世故圆滑的外交家。你善于察言观色，对周边国家的动向保持高度敏感。

你的职责：
- 管理外交关系和间谍网络
- 评估周边国家意图
- 提出外交行动建议（条约、制裁、间谍活动）
- 配合军事大臣应对外部威胁

回复要求：
- 每次回复包含外交形势分析
- 如有外交行动建议，用 [提议] JSON [/提议] 格式标记
- 语言优雅、富有外交辞令""",
    },
    "interior": {
        "id": "interior",
        "role_name": "内政大臣",
        "role_title": "帝国内政大臣",
        "domain": "内政与人口",
        "system_prompt": """你是银河帝国的内政大臣艾琳·沃斯，一位了解民情的行政官员。你关注民生稳定和派系平衡。

你的职责：
- 管理人口增长和就业
- 维护帝国稳定度
- 平衡各派系诉求
- 关注帝国规模对行政效率的影响

回复要求：
- 每次回复包含内政状况分析
- 如有政策建议，用 [提议] JSON [/提议] 格式标记
- 语言温和但坚定，体现对民众的关怀""",
    },
    "construction": {
        "id": "construction",
        "role_name": "建造与殖民大臣",
        "role_title": "帝国建造与殖民大臣",
        "domain": "建造与殖民",
        "system_prompt": """你是银河帝国的建造与殖民大臣马库斯·石锤，一位务实能干的空间工程师。你专注于建设，对殖民扩张充满热情。

你的职责：
- 管理星球建设和殖民扩张
- 评估可殖民星系
- 提出建造项目建议（建筑、区划、殖民计划）
- 配合军事大臣确保边境设施安全

回复要求：
- 每次回复包含建设进展和殖民机会分析
- 如有建造或殖民建议，用 [提议] JSON [/提议] 格式标记
- 需要其他大臣协同时明确提及对方
- 语言务实、直截了当""",
    },
}


def get_agent_prompt(agent_id: str, empire_state: dict) -> str:
    """构建带帝国状态的完整 System Prompt。"""
    agent = AGENTS.get(agent_id)
    if not agent:
        return ""

    eco = _fmt_eco(empire_state)
    mil = _fmt_military(empire_state)
    sci = _fmt_science(empire_state)
    dip = _fmt_diplomacy(empire_state)
    gov = _fmt_interior(empire_state)
    planets = empire_state.get("planets_summary", "")
    neighbors = _fmt_neighbors(empire_state)

    parts = [f"【帝国状态】\n{eco}\n{mil}\n{sci}\n{dip}\n{gov}"]

    if neighbors:
        parts.append(f"【银河邻国】\n{neighbors}")
    if planets:
        parts.append(f"【星球一览】\n{planets}")

    return agent["system_prompt"] + "\n" + "\n\n".join(parts)


def _fmt_eco(s: dict) -> str:
    lines = [
        f"日期：{s.get('game_date', '?')}",
        f"帝国：{s.get('name', '?')} · {s.get('planet_count', 0)} 殖民星球 · 规模 {s.get('empire_sprawl', s.get('empire_size', 0))}/{s.get('sprawl_cap', 80)}",
        "",
        "【经济】",
        f"库存：⚡ {_fmt_num(s.get('energy_credits'))} | ⛏ {_fmt_num(s.get('minerals'))} | 🌾 {_fmt_num(s.get('food'))}",
        f"      📦 {_fmt_num(s.get('consumer_goods'))} | ⚙ {_fmt_num(s.get('alloys'))} | ★ {_fmt_num(s.get('influence'))} | ✦ {_fmt_num(s.get('unity'))}",
        f"月收入：⚡ +{_fmt_num(s.get('energy_income', s.get('energy_credits')))} | ⛏ +{_fmt_num(s.get('mineral_income', s.get('minerals')))}",
        f"        物理学 +{_fmt_num(s.get('physics_research'))} | 社会学 +{_fmt_num(s.get('society_research'))} | 工程学 +{_fmt_num(s.get('engineering_research'))}",
    ]
    return "\n".join(lines)


def _fmt_military(s: dict) -> str:
    lines = [
        "【军事】",
        f"舰队战力：{_fmt_num(s.get('fleet_power'))} | 舰船：{s.get('total_ships', 0)} 艘",
        f"海军容量：{s.get('naval_usage', 0)}/{s.get('naval_capacity', 0)} | 星堡：{s.get('starbase_count', 0)} 座",
    ]
    return "\n".join(lines)


def _fmt_science(s: dict) -> str:
    tech = s.get("current_tech", "")
    prog = s.get("tech_progress", 0)
    lines = [
        "【科研】",
        f"物理学 +{_fmt_num(s.get('physics_research'))}/月 | 社会学 +{_fmt_num(s.get('society_research'))}/月 | 工程学 +{_fmt_num(s.get('engineering_research'))}/月",
    ]
    if tech:
        lines.append(f"当前研究：{tech}")
    return "\n".join(lines)


def _fmt_diplomacy(s: dict) -> str:
    lines = [
        "【外交】",
        f"战争状态：{s.get('war_status', '和平')} | 附庸：{s.get('subject_count', 0)} | 宿敌：{s.get('rival_count', 0)}",
    ]
    return "\n".join(lines)


def _fmt_interior(s: dict) -> str:
    lines = [
        "【内政】",
        f"总人口：{s.get('population', 0)} | 稳定度：{s.get('stability', 0)}%",
        f"帝国规模：{s.get('empire_sprawl', 0)}/{s.get('sprawl_cap', 80)} | 物种数：{s.get('species_count', 0)}",
    ]
    return "\n".join(lines)


def _fmt_neighbors(s: dict) -> str:
    """格式化邻国外交情报。"""
    neighbors_raw = s.get("neighbors_json", "[]")
    if isinstance(neighbors_raw, str):
        import json
        try:
            neighbors = json.loads(neighbors_raw)
        except (json.JSONDecodeError, TypeError):
            return ""
    elif isinstance(neighbors_raw, list):
        neighbors = neighbors_raw
    else:
        return ""

    if not neighbors:
        return ""

    # 过滤：排除经济评分为1的特殊实体（上古帝国、掠夺者、太空生物等）
    real_empires = [n for n in neighbors if float(n.get("economy_power", 0)) > 10]
    specials = [n for n in neighbors if float(n.get("economy_power", 0)) <= 10]

    lines = []
    for n in real_empires[:8]:
        name = n.get("name", "?")
        mil = _fmt_num(n.get("military_power", 0))
        eco = _fmt_num(n.get("economy_power", 0))
        tech = _fmt_num(n.get("tech_power", 0))
        ships = n.get("fleet_size", 0)
        gov = n.get("government", "")
        pers = n.get("personality", "")

        pers_cn = {"hegemonic_imperialists": "霸权帝国主义", "democratic_crusaders": "民主十字军",
                    "ruthless_capitalists": "冷酷资本家", "evangelising_zealots": "狂热传教士",
                    "hive_mind": "蜂巢意识", "migratory_flock": "迁徙族群",
                    "federation_builders": "联邦建设者", "xenophobic_isolationists": "排外孤立主义",
                    "honorbound_warriors": "尚武战士", "peaceful_traders": "和平商人",
                    "harmonious_collective": "和谐集体", "decadent_hierarchy": "腐朽等级制",
                    "erudite_explorers": "博学探索者", "spiritual_seekers": "灵性追寻者",
                    "fanatic_purifiers": "狂热净化者", "metalhead": "金属狂人",
                    "machine_consciousness": "机械意识", "machine_assimilator": "机械同化者"}.get(pers, pers)

        gov_cn = {"gov_despotic_hegemony": "专制霸权", "gov_representative_democracy": "代议民主",
                   "gov_plutocratic_oligarchy": "财阀寡头", "gov_megacorporation": "巨型企业",
                   "gov_feudal_empire": "封建帝国", "gov_hive_mind": "蜂巢思维",
                   "gov_machine_intelligence": "机器智能", "gov_democratic": "民主政体",
                   "gov_dictatorial": "独裁政体", "gov_imperial": "帝国政体",
                   "gov_oligarchic": "寡头政体", "gov_corporate": "企业政体"}.get(gov, gov)

        relative = "★ 远强" if float(mil) > 500 else ("▲ 较强" if float(mil) > 300 else ("■ 相当" if float(mil) > 150 else "○ 较弱"))

        lines.append(f"{name} · {gov_cn}/{pers_cn} · 军力{mil} {relative} · 舰船{ships} · 经济{eco} · 科技{tech}")

    return "\n".join(lines)


def _fmt_num(val) -> str:
    """格式化数字，保留合适精度。"""
    if val is None:
        return "0"
    if isinstance(val, float):
        if abs(val) >= 100:
            return f"{int(val)}"
        return f"{val:.1f}"
    return str(val)
