from aiohttp import ClientSession
from flogin import Plugin, Settings


class InvalidSettings(Exception): ...


class PluginSettings(Settings):
    webhooks: str | None


class DiscordPlugin(Plugin[PluginSettings]):
    session: ClientSession

    async def start(self) -> None:
        async with ClientSession() as cs:
            self.session = cs
            await super().start()

    @property
    def webhooks(self) -> dict[str, str]:
        try:
            raw = self.settings.webhooks or ""
            return {
                parts[0].strip(): parts[1].strip()
                for line in raw.strip().splitlines()
                if (parts := line.split("!"))
            }
        except Exception as e:
            raise InvalidSettings("Could not convert settings") from e
