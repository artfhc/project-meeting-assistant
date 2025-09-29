MEETING_SUMMARY_PROMPT = """Please analyze the following meeting transcript and create a structured summary using the format below.

Focus on extracting the most important information and organizing it clearly:

## Meeting Summary

### Key Points
- [List the main topics discussed and important information shared]

### Decisions
- [List any decisions that were made during the meeting]

### Action Items
- [List specific tasks assigned to individuals with deadlines if mentioned]

### Open Questions
- [List any unresolved questions or topics that need follow-up]

Transcript:
{transcript}

Please provide a concise but comprehensive summary following the format above."""

FOLLOW_UP_PROMPT = """Based on the meeting summary below, generate a list of follow-up actions and next steps:

{summary}

Please provide:
1. Immediate next steps (within 1-2 days)
2. Short-term actions (within 1 week)
3. Long-term actions (beyond 1 week)
4. People who should be informed about this meeting"""