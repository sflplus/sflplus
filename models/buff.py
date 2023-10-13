class Buff:
    """Represents a bud NFT buff"""

    def __init__(
        self,
        category: str,
        value: float,
        emoji: str,
        percentage: bool = False,
        extra: str = "",
    ) -> None:
        self.category: str = category
        self.value: float = value
        self.percentage: bool = percentage
        self.extra: str = extra
        self.emoji: str = emoji

    def multiply(self, multiplier: float) -> None:
        self.value = round(self.value * multiplier, 5)

    def __str__(self) -> str:
        if self.percentage:
            if self.extra:
                return (
                    f"{str(self.value)}% {self.extra} "
                    + f"{self.category} {self.emoji}"
                )
            return f"{str(self.value)}% {self.category} {self.emoji}"
        else:
            return f"+{str(self.value)} {self.category} {self.emoji}"

    def __repr__(self) -> str:
        if self.percentage:
            if self.extra:
                return f"Buff({str(self.value)}% {self.extra} {self.category})"
            return f"Buff({str(self.value)}% {self.category})"
        else:
            return f"Buff(+ {str(self.value)} {self.category})"
