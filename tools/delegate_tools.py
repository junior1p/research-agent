"""
delegate_tools.py - Shared knowledge base tools for sub-agents.

These tools allow sub-agents to:
- Read/write data to the shared JSON knowledge base
- Track task status and completion
- Store results for downstream agents
"""

import json
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Base paths
BASE_DIR = Path(__file__).parent.parent
SHARED_DIR = BASE_DIR / "shared"
RESULTS_DIR = BASE_DIR / "results"

# Ensure directories exist
SHARED_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


def _get_task_id() -> str:
    """Get current task ID from environment or generate one."""
    task_id = os.environ.get("RESEARCH_TASK_ID")
    if not task_id:
        task_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
        os.environ["RESEARCH_TASK_ID"] = task_id
    return task_id


def init_task(topic: str, task_id: Optional[str] = None) -> str:
    """
    Initialize a new research task.
    
    Args:
        topic: The research topic
        task_id: Optional custom task ID (auto-generated if not provided)
    
    Returns:
        The task ID
    """
    if task_id:
        os.environ["RESEARCH_TASK_ID"] = task_id
    else:
        task_id = _get_task_id()
    
    # Create task info
    task_info = {
        "task_id": task_id,
        "topic": topic,
        "created_at": datetime.now().isoformat(),
        "status": "initialized",
        "agents_completed": []
    }
    
    # Save task info to shared KB
    write_shared("task_info", task_info)
    
    # Create results subdirectory
    task_results_dir = RESULTS_DIR / task_id
    task_results_dir.mkdir(exist_ok=True)
    
    return task_id


def get_task_id() -> str:
    """Get the current task ID."""
    return _get_task_id()


def get_task_info(task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the research task info.
    
    Args:
        task_id: Optional task ID (uses current task if not provided)
    
    Returns:
        Task info dictionary
    """
    tid = task_id or _get_task_id()
    data = read_shared("task_info")
    
    if data and data.get("task_id") == tid:
        return data
    
    # Try to find task info file
    task_file = SHARED_DIR / f"task_{tid}_task_info.json"
    if task_file.exists():
        with open(task_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {
        "task_id": tid,
        "status": "unknown",
        "error": "Task info not found"
    }


def read_shared(agent_type: str, task_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Read the latest shared data for a given agent type.
    
    Args:
        agent_type: One of: 'literature', 'analysis', 'review', 'ideas', 'task_info'
        task_id: Optional task ID (uses current task if not provided)
    
    Returns:
        The shared data dictionary, or None if not found
    """
    tid = task_id or _get_task_id()
    
    # Mapping of agent_type to filename suffix
    type_to_suffix = {
        "literature": "literature_search",
        "analysis": "paper_analysis",
        "review": "literature_review",
        "ideas": "proposed_ideas",
        "task_info": "task_info",
    }
    
    suffix = type_to_suffix.get(agent_type, agent_type)
    filename = f"task_{tid}_{suffix}.json"
    filepath = SHARED_DIR / filename
    
    if not filepath.exists():
        # Try legacy naming without task_ prefix
        legacy_path = SHARED_DIR / f"{agent_type}.json"
        if legacy_path.exists():
            filepath = legacy_path
        else:
            return None
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return None


def write_shared(agent_type: str, data: Dict[str, Any], task_id: Optional[str] = None) -> str:
    """
    Write data to the shared knowledge base.
    
    Args:
        agent_type: One of: 'literature', 'analysis', 'review', 'ideas', 'task_info'
        data: The data dictionary to save
        task_id: Optional task ID (uses current task if not provided)
    
    Returns:
        Path to the saved file
    """
    tid = task_id or _get_task_id()
    
    # Mapping of agent_type to filename suffix
    type_to_suffix = {
        "literature": "literature_search",
        "analysis": "paper_analysis",
        "review": "literature_review",
        "ideas": "proposed_ideas",
        "task_info": "task_info",
    }
    
    suffix = type_to_suffix.get(agent_type, agent_type)
    filename = f"task_{tid}_{suffix}.json"
    filepath = SHARED_DIR / filename
    
    # Add metadata
    data["_meta"] = {
        "agent_type": agent_type,
        "task_id": tid,
        "saved_at": datetime.now().isoformat(),
        "file": str(filepath)
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def report_complete(agent_type: str, summary: str, task_id: Optional[str] = None) -> str:
    """
    Mark an agent's task as complete.
    
    Args:
        agent_type: The type of agent completing
        summary: Brief summary of what was accomplished
        task_id: Optional task ID (uses current task if not provided)
    
    Returns:
        Confirmation message
    """
    tid = task_id or _get_task_id()
    
    # Read current task info
    task_info = read_shared("task_info") or {}
    
    # Add to completed agents list
    if "agents_completed" not in task_info:
        task_info["agents_completed"] = []
    
    completion_record = {
        "agent": agent_type,
        "summary": summary,
        "completed_at": datetime.now().isoformat()
    }
    
    # Avoid duplicates
    existing = [a["agent"] for a in task_info["agents_completed"]]
    if agent_type not in existing:
        task_info["agents_completed"].append(completion_record)
    
    task_info["last_complete_agent"] = agent_type
    task_info["status"] = "in_progress"
    
    # Save updated task info
    write_shared("task_info", task_info)
    
    return f"Completed: {agent_type} - {summary}"


def list_shared_files(task_id: Optional[str] = None) -> List[str]:
    """
    List all shared files for a task.
    
    Args:
        task_id: Optional task ID (uses current task if not provided)
    
    Returns:
        List of filenames
    """
    tid = task_id or _get_task_id()
    prefix = f"task_{tid}_"
    
    return [f.name for f in SHARED_DIR.iterdir() if f.is_file() and f.name.startswith(prefix)]


def get_results_dir(task_id: Optional[str] = None) -> Path:
    """
    Get the results directory for a task.
    
    Args:
        task_id: Optional task ID (uses current task if not provided)
    
    Returns:
        Path to results directory
    """
    tid = task_id or _get_task_id()
    results = RESULTS_DIR / tid
    results.mkdir(exist_ok=True)
    return results


def write_result(filename: str, content: str, task_id: Optional[str] = None) -> str:
    """
    Write a result file to the results directory.
    
    Args:
        filename: Name of the result file
        content: Content to write
        task_id: Optional task ID (uses current task if not provided)
    
    Returns:
        Path to the written file
    """
    results = get_results_dir(task_id)
    filepath = results / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return str(filepath)
