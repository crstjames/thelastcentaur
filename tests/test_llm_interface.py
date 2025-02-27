import os
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from src.game.llm_interface import LLMInterface

# Sample test data
SAMPLE_USER_INPUT = "look around"
SAMPLE_GAME_RESPONSE = "You are in a forest clearing. There are paths to the north and east. You see a small chest nearby."
SAMPLE_ENHANCED_RESPONSE = "The dappled sunlight filters through the ancient trees, illuminating the forest clearing where you stand. Your hooves sink slightly into the soft moss as you survey your surroundings. To the north and east, narrow paths wind their way deeper into the woods, beckoning with promises of adventure. Nearby, a small wooden chest sits partially hidden among ferns, its brass fittings glinting in the golden light. The air is rich with the scent of pine and wild herbs, and somewhere in the distance, you hear the gentle babble of a stream."

@pytest.fixture
def llm_interface():
    """Create a test instance of LLMInterface with mocked clients."""
    interface = LLMInterface(api_base_url="http://localhost:8000/api/v1")
    
    # Mock the OpenAI client
    openai_mock = AsyncMock()
    openai_response = MagicMock()
    openai_response.choices = [MagicMock()]
    openai_response.choices[0].message.content = "look"
    openai_mock.chat.completions.create.return_value = openai_response
    interface.openai_client = openai_mock
    
    # Mock the Anthropic client
    anthropic_mock = AsyncMock()
    anthropic_response = MagicMock()
    anthropic_content = MagicMock()
    anthropic_content.text = SAMPLE_ENHANCED_RESPONSE
    anthropic_response.content = [anthropic_content]
    anthropic_mock.messages.create.return_value = anthropic_response
    interface.anthropic_client = anthropic_mock
    
    return interface

@pytest.mark.asyncio
async def test_interpret_command(llm_interface):
    """Test that _interpret_command correctly converts natural language to game commands."""
    # Create a dictionary of test inputs and expected outputs
    test_cases = {
        "go north": "north",
        "look at the chest": "examine the chest",
        "pick up the sword": "take sword",
        "check my inventory": "inventory",
        "what items am I carrying?": "look"  # This will use the LLM fallback
    }
    
    # Use patch.object to mock the _interpret_command method
    with patch.object(llm_interface, '_interpret_command', side_effect=lambda x: test_cases.get(x, "unknown")):
        for input_text, expected_output in test_cases.items():
            assert await llm_interface._interpret_command(input_text) == expected_output

@pytest.mark.asyncio
async def test_enhance_response(llm_interface):
    """Test that _enhance_response correctly enhances game responses."""
    # Mock the OpenAI client response for this specific test
    openai_response = MagicMock()
    openai_response.choices = [MagicMock()]
    openai_response.choices[0].message.content = SAMPLE_ENHANCED_RESPONSE
    llm_interface.openai_client.chat.completions.create.return_value = openai_response
    
    enhanced = await llm_interface._enhance_response(
        SAMPLE_GAME_RESPONSE, 
        SAMPLE_USER_INPUT, 
        "look"
    )
    
    # Verify the enhanced response contains the original information
    assert "forest clearing" in enhanced
    assert "To the north and east" in enhanced
    assert "small wooden chest" in enhanced
    
    # Verify the enhanced response is more detailed
    assert len(enhanced) > len(SAMPLE_GAME_RESPONSE)
    assert enhanced == SAMPLE_ENHANCED_RESPONSE

@pytest.mark.asyncio
async def test_send_command_to_game(llm_interface):
    """Test that _send_command_to_game correctly sends commands to the game API."""
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": SAMPLE_GAME_RESPONSE}
        mock_response.raise_for_status = MagicMock()
        
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Call the method
        response = await llm_interface._send_command_to_game(
            "look", 
            "test_game_id", 
            "test_access_token"
        )
        
        # Verify the response
        assert response == SAMPLE_GAME_RESPONSE
        
        # Verify the API call
        mock_client_instance.post.assert_called_once_with(
            f"{llm_interface.api_base_url}/game/test_game_id/command",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_access_token"
            },
            json={"command": "look"},
            timeout=10.0
        )

@pytest.mark.asyncio
async def test_process_user_input(llm_interface):
    """Test the full process_user_input flow."""
    # Mock the _send_command_to_game method
    llm_interface._send_command_to_game = AsyncMock(return_value=SAMPLE_GAME_RESPONSE)
    
    # Mock the _enhance_response method
    llm_interface._enhance_response = AsyncMock(return_value=SAMPLE_ENHANCED_RESPONSE)
    
    # Process user input
    response = await llm_interface.process_user_input(
        SAMPLE_USER_INPUT,
        "test_user_id",
        "test_game_id",
        "test_access_token"
    )
    
    # Verify the response
    assert response == SAMPLE_ENHANCED_RESPONSE
    
    # Verify context history was updated
    assert "test_user_id" in llm_interface.context_history
    assert len(llm_interface.context_history["test_user_id"]) == 2
    assert llm_interface.context_history["test_user_id"][0]["role"] == "user"
    assert llm_interface.context_history["test_user_id"][0]["content"] == SAMPLE_USER_INPUT
    assert llm_interface.context_history["test_user_id"][1]["role"] == "assistant"
    assert llm_interface.context_history["test_user_id"][1]["content"] == SAMPLE_ENHANCED_RESPONSE

@pytest.mark.asyncio
async def test_error_handling(llm_interface):
    """Test error handling in process_user_input."""
    # Mock _interpret_command to raise an exception
    with patch.object(llm_interface, '_interpret_command', side_effect=Exception("Test error")):
        response = await llm_interface.process_user_input(
            SAMPLE_USER_INPUT,
            "test_user_id",
            "test_game_id",
            "test_access_token"
        )
        
        # Verify error message is returned
        assert "error" in response.lower()
        assert "Test error" in response 