from openai import OpenAI
from datetime import datetime
from config.settings import Config
from .prompts import MEETING_SUMMARY_PROMPT

class OpenAISummarizer:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your .env file.")

        # Set up OpenAI client (modern API)
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def summarize_transcript(self, transcript):
        """Generate meeting summary from transcript using OpenAI"""
        if not transcript:
            return None, "No transcript provided"

        try:
            print("Generating summary with OpenAI...")
            prompt = MEETING_SUMMARY_PROMPT.format(transcript=transcript)

            # Use the modern OpenAI API format
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates structured meeting summaries. Focus on extracting key information and organizing it clearly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3  # Lower temperature for more focused, consistent outputs
            )

            summary = response.choices[0].message.content.strip()

            # Save summary to file
            summary_filepath = self._save_summary(summary)

            return summary, summary_filepath

        except Exception as e:
            # Handle various OpenAI API errors
            error_msg = f"Error generating summary with OpenAI: {e}"
            print(error_msg)

            # Check for common error types
            if "authentication" in str(e).lower():
                error_msg = "OpenAI API authentication failed. Please check your API key."
            elif "rate limit" in str(e).lower():
                error_msg = "OpenAI API rate limit exceeded. Please try again later."
            elif "invalid request" in str(e).lower():
                error_msg = f"OpenAI API request error: {e}"

            return None, error_msg

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