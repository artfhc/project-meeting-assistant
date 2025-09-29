import re

class TranscriptCleaner:
    @staticmethod
    def clean_transcript(text):
        """Clean and format transcript text"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common filler words (optional)
        filler_words = ['um', 'uh', 'er', 'ah', 'like', 'you know']
        for filler in filler_words:
            text = re.sub(rf'\b{filler}\b', '', text, flags=re.IGNORECASE)

        # Clean up punctuation spacing
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        text = re.sub(r'([,.!?])\s*', r'\1 ', text)

        # Capitalize first letter of sentences
        text = re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def add_timestamps(text, duration_seconds=None):
        """Add approximate timestamps to transcript (basic implementation)"""
        if not text or not duration_seconds:
            return text

        sentences = text.split('. ')
        if len(sentences) <= 1:
            return text

        time_per_sentence = duration_seconds / len(sentences)
        timestamped_text = ""

        for i, sentence in enumerate(sentences):
            timestamp = int(i * time_per_sentence)
            minutes = timestamp // 60
            seconds = timestamp % 60
            timestamped_text += f"[{minutes:02d}:{seconds:02d}] {sentence.strip()}"
            if i < len(sentences) - 1:
                timestamped_text += ".\n\n"

        return timestamped_text