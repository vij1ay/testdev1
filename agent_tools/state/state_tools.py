from typing import Dict, Optional, Any
from langchain_core.tools import tool

# In-memory state storage per conversation thread
conversation_state: Dict[str, Dict[str, Any]] = {}


@tool
def store_conversation_data(thread_id: str, key: str, value: Any) -> dict:
    """Store important data (like IDs) for later use in the conversation.
    Use this to remember customer_id, specialist_id, appointment details, etc."""

    from langchain_core.runnables import ensure_config
    config = ensure_config()
    thread_id = config.get("configurable", {}).get("thread_id", "unknown")

    if thread_id not in conversation_state:
        conversation_state[thread_id] = {}

    conversation_state[thread_id][key] = value

    print(f"\n[STATE] Stored {key}: {value} for thread {thread_id}")

    return {
        "message": f"Stored {key} successfully",
        "stored_data": {key: value},
        "all_stored_data": conversation_state[thread_id]
    }


@tool
def get_conversation_data(thread_id: str, key: Optional[str] = None) -> dict:
    """Retrieve previously stored conversation data by key, or get all data if no key specified."""

    if thread_id not in conversation_state:
        return {"message": "No data stored for this conversation", "data": {}}

    if key:
        value = conversation_state[thread_id].get(key)
        if value is not None:
            print(f"\n[STATE] Retrieved {key}: {value} for thread {thread_id}")
            return {"message": f"Retrieved {key}", "data": {key: value}}
        else:
            return {"message": f"No data found for key: {key}", "data": {}}
    else:
        print(
            f"\n[STATE] Retrieved all data for thread {thread_id}: {conversation_state[thread_id]}")
        return {"message": "Retrieved all stored data", "data": conversation_state[thread_id]}


@tool
def clear_conversation_data(thread_id: str) -> dict:
    """Clear all stored data for a conversation thread."""
    if thread_id in conversation_state:
        del conversation_state[thread_id]
        return {"message": "All conversation data cleared"}
    return {"message": "No data to clear"}
