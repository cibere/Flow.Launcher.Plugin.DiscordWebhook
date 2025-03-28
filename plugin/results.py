from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Unpack

from discord import DiscordException, Webhook
from flogin import Result as _Result
from flogin import ResultConstructorKwargs

if TYPE_CHECKING:
    from .core import DiscordPlugin  # noqa: F401


class Result(_Result["DiscordPlugin"]):
    def __init__(self, **kwargs: Unpack[ResultConstructorKwargs]) -> None:
        if "icon" not in kwargs:
            kwargs["icon"] = "assets/app.png"
        super().__init__(**kwargs)


class DisplayWebhookResult(Result):
    def __init__(
        self, keyword: str, name: str, **kwargs: Unpack[ResultConstructorKwargs]
    ) -> None:
        self.new_query = kwargs["auto_complete_text"] = f"{keyword} {name} "
        self.name = name
        super().__init__(**kwargs)

    async def callback(self):
        assert self.plugin

        await self.plugin.api.change_query(self.new_query)
        return False

    async def context_menu(self):
        assert self.plugin

        return RemoveWebhookResult(self.name, title="Remove Webhook")


class RemoveWebhookResult(Result):
    def __init__(self, name: str, **kwargs: Unpack[ResultConstructorKwargs]) -> None:
        self.name = name
        super().__init__(**kwargs)

    async def callback(self):
        assert self.plugin

        self.plugin.settings.webhooks = "\n".join(
            line
            for line in (self.plugin.settings.webhooks or "").splitlines()
            if not line.replace(" ", "").startswith(f"{self.name}!")
        )
        await self.plugin.api.show_notification(
            "Discord Webhook",
            f"Removed the {self.name} webhook. Note: for this to take affect, you must query the plugin again.",
        )
        return False


class SendMessageResult(Result):
    def __init__(self, url: str, message: str) -> None:
        self.url = url
        self.message = message

        super().__init__(
            title=f"Do you want to send the message to {url}?",
            sub=f"Message: {message}",
        )

    async def callback(self):
        assert self.plugin
        assert self.plugin.last_query

        hook = Webhook.from_url(self.url, session=self.plugin.session)
        try:
            msg = await hook.send(self.message, wait=True)
        except DiscordException as e:
            res = Result(
                title="An occured while attempting to send the message.", sub=str(e)
            )
        else:
            res = Result.create_with_partial(
                partial(self.plugin.api.open_url, msg.jump_url),
                title="Message sent successfully",
                sub=f"ID: {msg.id}",
            )

        await self.plugin.last_query.update_results([res])
        return False
