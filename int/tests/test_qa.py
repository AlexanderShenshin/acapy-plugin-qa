"""Status Request and response tests"""

from echo_agent.client import EchoClient
from echo_agent.models import ConnectionInfo
import pytest
import httpx

import logging

LOGGER = logging.getLogger(__name__)

thread_id = "MockTestRequestID"
question = {
    "@type": "https://didcomm.org/questionanswer/1.0/question",
    "@id": thread_id,
    "question_text": "Are you a test agent?",
    "question_detail": "Verifying that the Q&A Handler works via integration tests",
    "valid_responses": [{"text": "yes"}, {"text": "no"}],
}


@pytest.mark.asyncio
async def test_send_question_receive_answer(
    echo: EchoClient, backchannel_endpoint: str, connection: ConnectionInfo
):
    """Test ACA-Py can respond to a question."""

    await echo.send_message(
        connection,
        question,
    )

    r = httpx.get(f"{backchannel_endpoint}/qa/get-questions")
    assert r.status_code == 200

    response = r.json()["results"][0]
    assert response["question_text"] == question["question_text"]
    assert response["question_detail"] == question["question_detail"]
    assert response["valid_responses"] == question["valid_responses"]

    answer = {
        "response": "yes",
    }
    question_id = response["_id"]
    r = httpx.post(f"{backchannel_endpoint}/qa/{question_id}/send-answer", json=answer)
    assert r.status_code == 200

    response = await echo.get_message(connection)

    assert response["@type"] == (
        "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/questionanswer/1.0/answer"
    )
    assert response["response"] == "yes"

    r = httpx.get(f"{backchannel_endpoint}/qa/get-questions")
    assert r.status_code == 200
    assert r.json()["results"] == []


@pytest.mark.asyncio
async def test_receive_question(
    echo: EchoClient,
    backchannel_endpoint: str,
    connection: ConnectionInfo,
    connection_id: str,
):
    """Test ACA-Py can send a question and receive an answer."""
    r = httpx.post(
        f"{backchannel_endpoint}/qa/{connection_id}/send-question", json=question
    )
    assert r.status_code == 200

    response = await echo.get_message(connection)
    assert response["@type"] == (
        "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/questionanswer/1.0/question"
    )
    thread_id = response["~thread"]["thid"]

    await echo.send_message(
        connection,
        {
            "@type": "https://didcomm.org/questionanswer/1.0/answer",
            "response": "yes",
            "~thread": {"thid": thread_id},
        },
    )
    r = httpx.get(f"{backchannel_endpoint}/qa/get-questions")
    assert r.status_code == 200
    assert r.json()["results"] == []
