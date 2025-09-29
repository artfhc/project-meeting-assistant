import re
from datetime import datetime
from config.settings import Config

class LocalMeetingSummarizer:
    def __init__(self):
        pass

    def summarize_transcript(self, transcript):
        """Generate meeting summary from transcript using rule-based approach"""
        if not transcript:
            return None, "No transcript provided"

        try:
            print("Generating summary using local text processing...")

            # Clean and process the transcript
            cleaned_text = self._clean_text(transcript)

            # Extract key information
            key_points = self._extract_key_points(cleaned_text)
            decisions = self._extract_decisions(cleaned_text)
            action_items = self._extract_action_items(cleaned_text)
            questions = self._extract_questions(cleaned_text)

            # Generate structured summary
            summary = self._format_summary(key_points, decisions, action_items, questions)

            # Save summary to file
            summary_filepath = self._save_summary(summary)

            return summary, summary_filepath

        except Exception as e:
            error_msg = f"Error generating summary: {e}"
            print(error_msg)
            return None, error_msg

    def _clean_text(self, text):
        """Clean and normalize the text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _extract_key_points(self, sentences):
        """Extract key discussion points"""
        key_indicators = [
            'discuss', 'talk about', 'mentioned', 'important', 'focus on',
            'main point', 'key', 'primary', 'significant', 'noted that',
            'explained', 'described', 'overview', 'summary', 'highlighted'
        ]

        key_points = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in key_indicators):
                if len(sentence) > 20:  # Filter out very short sentences
                    key_points.append(sentence.strip())

        # Limit to most relevant points
        return key_points[:5] if key_points else ["No specific key points identified"]

    def _extract_decisions(self, sentences):
        """Extract decisions made during the meeting"""
        decision_indicators = [
            'decided', 'agreed', 'concluded', 'determined', 'resolved',
            'settled on', 'chose to', 'will go with', 'final decision',
            'approved', 'accepted', 'confirmed'
        ]

        decisions = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in decision_indicators):
                if len(sentence) > 15:
                    decisions.append(sentence.strip())

        return decisions[:3] if decisions else ["No specific decisions identified"]

    def _extract_action_items(self, sentences):
        """Extract action items and tasks"""
        action_indicators = [
            'will', 'should', 'need to', 'must', 'have to', 'going to',
            'action item', 'task', 'todo', 'follow up', 'next step',
            'assign', 'responsible for', 'deadline', 'by next', 'complete'
        ]

        action_items = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in action_indicators):
                if len(sentence) > 15:
                    action_items.append(sentence.strip())

        return action_items[:5] if action_items else ["No specific action items identified"]

    def _extract_questions(self, sentences):
        """Extract open questions"""
        questions = []

        # Look for actual question marks
        for sentence in sentences:
            if '?' in sentence and len(sentence) > 10:
                questions.append(sentence.strip())

        # Look for question indicators
        question_indicators = [
            'question', 'unclear', 'unsure', 'not sure', 'wonder',
            'need to find out', 'follow up on', 'investigate',
            'what about', 'how do we', 'should we', 'what if'
        ]

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in question_indicators):
                if len(sentence) > 15:
                    questions.append(sentence.strip())

        return questions[:3] if questions else ["No open questions identified"]

    def _format_summary(self, key_points, decisions, action_items, questions):
        """Format the extracted information into a structured summary"""
        summary = "## Meeting Summary\n\n"

        summary += "### Key Points\n"
        for point in key_points:
            summary += f"- {point}\n"
        summary += "\n"

        summary += "### Decisions\n"
        for decision in decisions:
            summary += f"- {decision}\n"
        summary += "\n"

        summary += "### Action Items\n"
        for action in action_items:
            summary += f"- {action}\n"
        summary += "\n"

        summary += "### Open Questions\n"
        for question in questions:
            summary += f"- {question}\n"

        return summary

    def _save_summary(self, summary):
        """Save summary to markdown file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.md"
        filepath = f"{Config.SUMMARY_DIR}/{filename}"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"Summary saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving summary: {e}")
            return None