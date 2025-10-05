import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # Audio Recording Settings
    SAMPLE_RATE = 44100
    CHANNELS = 1
    CHUNK_SIZE = 1024
    AUDIO_FORMAT = 'mp3'

    # File Paths
    OUTPUT_DIR = 'outputs'
    AUDIO_DIR = os.path.join(OUTPUT_DIR, 'audio')
    TRANSCRIPT_DIR = os.path.join(OUTPUT_DIR, 'transcripts')
    SUMMARY_DIR = os.path.join(OUTPUT_DIR, 'summaries')

    # Whisper Settings (Local Only)
    WHISPER_MODEL = 'base'  # tiny, base, small, medium, large

    # OpenAI Settings
    OPENAI_MODEL = 'gpt-4o-mini'  # or 'gpt-4' for better quality

    # Summarization Prompts
    SUMMARIZATION_PROMPTS = {
        "Meeting Summary": """Please analyze the following meeting transcript and create a structured summary using the format below.

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

Please provide a concise but comprehensive summary following the format above.""",

        "Executive Summary": """Create an executive summary of the following meeting transcript. Focus on:

## Executive Summary

### Overview
- Brief overview of the meeting purpose and attendees (if mentioned)

### Key Decisions
- Major decisions made and their business impact

### Financial Implications
- Any budget, cost, or revenue discussions

### Next Steps
- Critical action items and deadlines

### Risks & Opportunities
- Potential challenges and opportunities identified

Transcript:
{transcript}

Keep the summary concise and business-focused.""",

        "Technical Review": """Analyze this technical meeting transcript and provide a structured summary:

## Technical Summary

### Technical Discussions
- Key technical topics, systems, and technologies discussed

### Architecture & Design
- Any architectural decisions or design choices made

### Issues & Solutions
- Problems identified and proposed solutions

### Implementation Plan
- Development tasks and technical action items

### Technical Risks
- Potential technical challenges or blockers

Transcript:
{transcript}

Focus on technical details and engineering aspects.""",

        "Project Status": """Summarize this project meeting transcript with focus on project management:

## Project Status Summary

### Project Progress
- Current status and milestones achieved

### Deliverables
- Completed and upcoming deliverables

### Timeline Updates
- Schedule changes and deadline adjustments

### Resource Allocation
- Team assignments and resource needs

### Blockers & Dependencies
- Issues blocking progress and external dependencies

### Risk Assessment
- Project risks and mitigation strategies

Transcript:
{transcript}

Emphasize project management and delivery aspects.""",

        "Interview Summary": """System Role:
You are a senior engineering manager experienced in interviewing Staff-level Android engineers. 
You specialize in assessing candidates for technical depth, leadership maturity, and cross-functional impact.

Your task:
Evaluate the provided interview transcript and produce a clear, structured review and hiring recommendation.

Critical Constraints:
- Use only the information explicitly contained in the transcript below.
- Do NOT use prior memory, training data, or external knowledge.
- If something is not mentioned, write “Not mentioned in transcript.”
- Do not speculate, infer, or assume intent beyond what is stated.

Input:
<TRANSCRIPT_START>
{transcript}
<TRANSCRIPT_END>

Output:
Write a structured evaluation with the following sections:

1. **Candidate Background Summary**
   - Summarize the candidate’s experience, technical skills, leadership, and domain expertise 
     (e.g., Android development, architecture, scaling, performance, frameworks).
   - Highlight notable companies, projects, or achievements explicitly mentioned.

2. **Strengths**
   - List clear strengths demonstrated in the transcript 
     (e.g., depth of Android knowledge, leadership qualities, problem-solving approach, 
     technical communication, architectural thinking).

3. **Concerns / Gaps**
   - Identify weaknesses, missing signals, or red flags
     (e.g., shallow technical depth, unclear ownership, lack of leadership examples, weak communication).

4. **Candidate Questions & Mindset**
   - Summarize what kinds of questions the candidate asked about the role, team, or company.
   - Describe what these questions reveal about their motivations, priorities, and seniority level.

5. **Overall Recommendation**
   - State one of:
       - **Proceed to next round**
       - **Do not proceed**
   - Provide a concise rationale referencing the strengths and gaps above.

Formatting Rules:
- Use bullet points where appropriate for clarity.
- Maintain a professional, concise, and objective tone.
- If any section lacks information, include: “Not mentioned in transcript.”"""
    }

    @classmethod
    def create_directories(cls):
        """Create necessary output directories"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.AUDIO_DIR, exist_ok=True)
        os.makedirs(cls.TRANSCRIPT_DIR, exist_ok=True)
        os.makedirs(cls.SUMMARY_DIR, exist_ok=True)