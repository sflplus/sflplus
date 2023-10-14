from models.buff import Buff

type_buffs: dict[str, dict[str, float | str]] = {
    "Plaza": {"category": "Basic Crops", "value": 0.2, "emoji": "🍃"},
    "Woodlands": {"category": "Wood", "value": 0.2, "emoji": "🌲"},
    "Cave": {"category": "Minerals", "value": 0.2, "emoji": "⚪"},
    "Sea": {
        "category": "Fish",
        "value": 10,
        "extra": "chance + 1",
        "emoji": "🐟",
    },
    "Castle": {"category": "Medium Crops", "value": 0.3, "emoji": "🍂"},
    "Port": {"category": "Eating Fish XP", "value": 10, "emoji": "🐠"},
    "Retreat": {"category": "Animal Produce", "value": 0.2, "emoji": "🐾"},
    "Saphiro": {"category": "Crop Speed", "value": 10, "emoji": "⏩"},
    "Snow": {"category": "Advanced Crops", "value": 0.3, "emoji": "🍁"},
    "Beach": {"category": "Fruit", "value": 0.2, "emoji": "🍒"},
}

stem_buffs: dict[str, dict[str, float | str]] = {
    "3 Leaf Clover": {"category": "Crops", "value": 0.5, "emoji": "🍃🍂🍁"},
    "Fish Hat": {
        "category": "Fish",
        "value": 10,
        "extra": "chance + 1",
        "emoji": "🐟",
    },
    "Diamond Gem": {"category": "Minerals", "value": 0.2, "emoji": "⚪🟠🟡"},
    "Gold Gem": {"category": "Gold", "value": 0.2, "emoji": "🟡"},
    "Miner Hat": {"category": "Iron", "value": 0.2, "emoji": "🟠"},
    "Carrot Head": {"category": "Carrots", "value": 0.3, "emoji": "🥕"},
    "Basic Leaf": {"category": "Basic Crops", "value": 0.2, "emoji": "🍃"},
    "Sunflower Hat": {"category": "Sunflowers", "value": 0.5, "emoji": "🌻"},
    "Ruby Gem": {"category": "Stone", "value": 0.2, "emoji": "⚪"},
    "Mushroom": {"category": "Mushrooms", "value": 0.3, "emoji": "🍄"},
    "Magic Mushrooms": {
        "category": "Magic Mushrooms",
        "value": 0.2,
        "emoji": "🍄✨",
    },
    "Acorn Hat": {"category": "Wood", "value": 0.1, "emoji": "🌲"},
    "Banana": {"category": "Fruit", "value": 0.2, "emoji": "🍒"},
    "Tree Hat": {"category": "Wood", "value": 0.2, "emoji": "🌲"},
    "Egg Head": {"category": "Egg", "value": 0.2, "emoji": "🥚"},
    "Apple Head": {"category": "Fruit", "value": 0.2, "emoji": "🍒"},
}

aura_buffs: dict[str, float] = {
    "Basic": 1.05,
    "Green": 1.2,
    "Rare": 2.0,
    "Mythical": 5.0,
}


class Bud:
    """Represents a bud NFT"""

    def __init__(
        self, id: int, color: str, ears: str, type: str, aura: str, stem: str
    ) -> None:
        self.id: int = id
        self.color: str = color
        self.ears: str = ears
        self.type: str = type
        self.aura: str = aura
        self.stem: str = stem
        self._compute_buffs()

    def _compute_buffs(self) -> None:
        self.buffs: list[Buff] = []
        aura: float = aura_buffs.get(self.aura, 1.0)

        tmp: dict = type_buffs[self.type]
        type_buff: Buff = Buff(
            tmp["category"],
            tmp["value"],
            tmp["emoji"],
            tmp["value"] > 1,
            tmp.get("extra", ""),
        )
        type_buff.multiply(aura)
        self.buffs.append(type_buff)

        _stem: dict | None = stem_buffs.get(self.stem, None)
        if _stem is None:
            return
        stem_buff: Buff = Buff(
            _stem["category"],
            _stem["value"],
            _stem["emoji"],
            _stem["value"] > 1,
            _stem.get("extra", ""),
        )
        stem_buff.multiply(aura)
        self.buffs.append(stem_buff)
