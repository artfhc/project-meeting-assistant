"""
Pydantic v2 models used across the Meeting Assistant backend.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class MeetingStatus(str, Enum):
    created = "created"
    recording = "recording"
    recorded = "recorded"
    transcribing = "transcribing"
    transcribed = "transcribed"
    summarizing = "summarizing"
    done = "done"
    error = "error"


class Meeting(BaseModel):
    id: str
    title: str
    created_at: str
    duration_s: int | None
    audio_path: str | None
    transcript_path: str | None
    summary_path: str | None
    transcript: str | None
    summary: str | None
    prompt_key: str | None
    status: MeetingStatus
    error_msg: str | None


class MeetingCreate(BaseModel):
    title: str = ""
    prompt_key: str | None = None


class MeetingUpdate(BaseModel):
    title: str | None = None
    prompt_key: str | None = None


class JobProgress(BaseModel):
    type: str = "job_progress"
    job_id: str
    meeting_id: str
    stage: str  # transcribing | cleaning | summarizing | done | error
    progress: int  # 0-100
    message: str


class SettingsModel(BaseModel):
    openai_api_key: str = ""
    whisper_model: str = "base"
    audio_device_index: int = -1
    output_dir: str = ""
    default_prompt_key: str = ""
    theme: str = "dark"


class AudioDevice(BaseModel):
    index: int
    name: str
