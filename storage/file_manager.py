import os
import json
from datetime import datetime
from config.settings import Config

class FileManager:
    def __init__(self):
        # Ensure directories exist
        Config.create_directories()

    def save_summary_as_markdown(self, summary, custom_filename=None):
        """Save summary as markdown file with custom filename"""
        if custom_filename:
            # Ensure .md extension
            if not custom_filename.endswith('.md'):
                custom_filename += '.md'
            filepath = os.path.join(Config.SUMMARY_DIR, custom_filename)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{timestamp}.md"
            filepath = os.path.join(Config.SUMMARY_DIR, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(summary)
            return filepath
        except Exception as e:
            print(f"Error saving markdown file: {e}")
            return None

    def save_summary_as_text(self, summary, custom_filename=None):
        """Save summary as text file with custom filename"""
        if custom_filename:
            # Ensure .txt extension
            if not custom_filename.endswith('.txt'):
                custom_filename += '.txt'
            filepath = os.path.join(Config.SUMMARY_DIR, custom_filename)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{timestamp}.txt"
            filepath = os.path.join(Config.SUMMARY_DIR, filename)

        try:
            # Remove markdown formatting for text file
            text_content = self._strip_markdown(summary)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return filepath
        except Exception as e:
            print(f"Error saving text file: {e}")
            return None

    def _strip_markdown(self, text):
        """Remove basic markdown formatting"""
        import re
        # Remove headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        # Remove bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Remove bullet points
        text = re.sub(r'^\s*[-*]\s*', '- ', text, flags=re.MULTILINE)
        return text

    def get_recent_files(self, file_type='all', limit=10):
        """Get list of recent files by type"""
        files = []

        if file_type in ['all', 'audio']:
            files.extend(self._get_files_from_dir(Config.AUDIO_DIR, '.wav'))

        if file_type in ['all', 'transcript']:
            files.extend(self._get_files_from_dir(Config.TRANSCRIPT_DIR, '.txt'))

        if file_type in ['all', 'summary']:
            files.extend(self._get_files_from_dir(Config.SUMMARY_DIR, ['.md', '.txt']))

        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        return files[:limit]

    def _get_files_from_dir(self, directory, extensions):
        """Get files with specific extensions from directory"""
        if not os.path.exists(directory):
            return []

        files = []
        if isinstance(extensions, str):
            extensions = [extensions]

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and any(filename.endswith(ext) for ext in extensions):
                files.append(filepath)

        return files

    def read_file(self, filepath):
        """Read content from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None

    def delete_file(self, filepath):
        """Delete a file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")
            return False