import json
import os
from datetime import datetime
from config.settings import Config

class MeetingDatabase:
    def __init__(self):
        self.db_file = os.path.join(Config.OUTPUT_DIR, 'meetings.json')
        self.meetings = self._load_database()

    def _load_database(self):
        """Load meetings database from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading database: {e}")
                return {"meetings": []}
        return {"meetings": []}

    def _save_database(self):
        """Save meetings database to JSON file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.meetings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving database: {e}")

    def add_meeting(self, audio_file, transcript_file, summary_file, duration=None):
        """Add a new meeting record to the database"""
        meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        meeting = {
            "id": meeting_id,
            "timestamp": datetime.now().isoformat(),
            "audio_file": audio_file,
            "transcript_file": transcript_file,
            "summary_file": summary_file,
            "duration": duration,
            "title": f"Meeting {meeting_id}"
        }

        self.meetings["meetings"].append(meeting)
        self._save_database()
        return meeting_id

    def get_meeting(self, meeting_id):
        """Get a specific meeting by ID"""
        for meeting in self.meetings["meetings"]:
            if meeting["id"] == meeting_id:
                return meeting
        return None

    def get_all_meetings(self):
        """Get all meetings sorted by timestamp (newest first)"""
        meetings = self.meetings["meetings"]
        return sorted(meetings, key=lambda x: x["timestamp"], reverse=True)

    def update_meeting_title(self, meeting_id, title):
        """Update the title of a meeting"""
        for meeting in self.meetings["meetings"]:
            if meeting["id"] == meeting_id:
                meeting["title"] = title
                self._save_database()
                return True
        return False

    def delete_meeting(self, meeting_id):
        """Delete a meeting record"""
        self.meetings["meetings"] = [
            m for m in self.meetings["meetings"] if m["id"] != meeting_id
        ]
        self._save_database()

    def search_meetings(self, query):
        """Search meetings by title or content"""
        results = []
        query_lower = query.lower()

        for meeting in self.meetings["meetings"]:
            if query_lower in meeting["title"].lower():
                results.append(meeting)

        return results