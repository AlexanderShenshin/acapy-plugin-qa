from aries_cloudagent.messaging.base_handler import BaseHandler
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.responder import BaseResponder

from ..messages.answer import Answer


class AnswerHandler(BaseHandler):
    """Handler for Answer message."""

    # TODO: check these variables
    RECEIVED_TOPIC = "acapy::questionanswer::received"
    WEBHOOK_TOPIC = "acapy::webhook::questionanswer"

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Handle answer message."""

        """Handle question message."""
        # print(context.message)
        # await responder.send_reply(context.message)
        assert isinstance(context.message, Answer)
        self._logger.debug(
            "Received answer in thread %s " "with text: %s",
            context.message._thread,
            context.message.response,
        )
        # Emit a webhook
        await context.profile.notify(
            self.WEBHOOK_TOPIC,
            {
                "thread_id": context.message._thread,
                "response": context.message.response,
            },
        )

        # Emit an event
        await context.profile.notify(
            self.RECEIVED_TOPIC,
            {
                "thread_id": context.message._thread,
                "response": context.message.response,
            },
        )
