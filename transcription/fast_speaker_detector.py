import numpy as np
import librosa
import warnings

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError as e:
    print(f"Resemblyzer not available: {e}")
    RESEMBLYZER_AVAILABLE = False

try:
    from sklearn.cluster import AgglomerativeClustering
    SKLEARN_AVAILABLE = True
except ImportError as e:
    print(f"scikit-learn not available: {e}")
    SKLEARN_AVAILABLE = False

try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError as e:
    print(f"webrtcvad not available: {e}")
    WEBRTCVAD_AVAILABLE = False

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

class FastSpeakerDetector:
    def __init__(self):
        """Initialize Resemblyzer-based fast speaker detection"""
        self.encoder = None
        self._load_encoder()

    def _load_encoder(self):
        """Load Resemblyzer voice encoder"""
        if not RESEMBLYZER_AVAILABLE:
            print("Resemblyzer not available - speaker detection disabled")
            print("Install with: pip install resemblyzer>=0.1.1")
            self.encoder = None
            return

        try:
            print("Loading Resemblyzer voice encoder...")
            self.encoder = VoiceEncoder()
            print("Resemblyzer encoder loaded successfully!")
        except Exception as e:
            print(f"Error loading Resemblyzer encoder: {e}")
            self.encoder = None

    def detect_voice_activity(self, audio, sample_rate, frame_duration_ms=30):
        """
        Detect voice activity using WebRTC VAD
        Returns list of (start_time, end_time) tuples for speech segments
        """
        try:
            vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3 (2 = moderate)

            frame_size = int(sample_rate * frame_duration_ms / 1000)
            speech_segments = []

            # Process audio in frames
            current_speech_start = None

            for i in range(0, len(audio) - frame_size, frame_size):
                frame = audio[i:i + frame_size]

                # Convert to 16-bit PCM for WebRTC VAD
                frame_16bit = (frame * 32767).astype(np.int16).tobytes()

                # Check if frame contains speech
                is_speech = vad.is_speech(frame_16bit, sample_rate)

                current_time = i / sample_rate

                if is_speech and current_speech_start is None:
                    # Start of speech segment
                    current_speech_start = current_time
                elif not is_speech and current_speech_start is not None:
                    # End of speech segment
                    speech_segments.append((current_speech_start, current_time))
                    current_speech_start = None

            # Handle case where speech continues to end of audio
            if current_speech_start is not None:
                speech_segments.append((current_speech_start, len(audio) / sample_rate))

            # Merge nearby segments (within 0.5 seconds)
            merged_segments = []
            for start, end in speech_segments:
                if merged_segments and start - merged_segments[-1][1] < 0.5:
                    # Merge with previous segment
                    merged_segments[-1] = (merged_segments[-1][0], end)
                else:
                    merged_segments.append((start, end))

            return merged_segments

        except Exception as e:
            print(f"VAD failed, using simple energy-based detection: {e}")
            return self._simple_voice_detection(audio, sample_rate)

    def _simple_voice_detection(self, audio, sample_rate):
        """Simple energy-based voice activity detection fallback"""
        # Calculate energy in 1-second windows
        window_size = sample_rate
        energy_threshold = np.mean(audio**2) * 2  # Adaptive threshold

        speech_segments = []
        current_start = None

        for i in range(0, len(audio), window_size):
            window = audio[i:i + window_size]
            energy = np.mean(window**2)

            time_start = i / sample_rate
            time_end = min((i + window_size) / sample_rate, len(audio) / sample_rate)

            if energy > energy_threshold and current_start is None:
                current_start = time_start
            elif energy <= energy_threshold and current_start is not None:
                speech_segments.append((current_start, time_end))
                current_start = None

        if current_start is not None:
            speech_segments.append((current_start, len(audio) / sample_rate))

        return speech_segments

    def detect_speakers(self, audio_filepath, progress_callback=None, max_speakers=10):
        """
        Fast speaker detection using Resemblyzer
        Returns list of speaker segments: [{'start': time, 'end': time, 'speaker': 'Speaker_XX'}]
        """
        if not self.encoder:
            print("Resemblyzer encoder not available")
            return []

        try:
            if progress_callback:
                progress_callback("Loading audio for speaker detection...", 0)

            # Load audio
            print(f"Loading audio: {audio_filepath}")
            audio, sample_rate = librosa.load(audio_filepath, sr=16000)
            duration = len(audio) / sample_rate
            print(f"Audio loaded: {duration:.1f}s at {sample_rate}Hz")

            if progress_callback:
                progress_callback("Detecting voice activity...", 10)

            # Step 1: Voice Activity Detection
            print("Detecting voice activity...")
            speech_segments = self.detect_voice_activity(audio, sample_rate)
            print(f"Found {len(speech_segments)} speech segments")

            if not speech_segments:
                print("No speech detected in audio")
                return []

            if progress_callback:
                progress_callback("Extracting speaker embeddings...", 30)

            # Step 2: Extract embeddings for each speech segment
            print("Extracting speaker embeddings...")
            embeddings = []
            segment_info = []

            for i, (start_time, end_time) in enumerate(speech_segments):
                if progress_callback:
                    progress = 30 + int((i / len(speech_segments)) * 40)
                    progress_callback(f"Processing segment {i+1}/{len(speech_segments)}...", progress)

                # Extract audio segment
                start_sample = int(start_time * sample_rate)
                end_sample = int(end_time * sample_rate)
                segment_audio = audio[start_sample:end_sample]

                # Skip very short segments (< 0.5 seconds)
                if len(segment_audio) < sample_rate * 0.5:
                    continue

                try:
                    # Preprocess for Resemblyzer
                    processed_wav = preprocess_wav(segment_audio, sample_rate)

                    # Extract embedding
                    embedding = self.encoder.embed_utterance(processed_wav)

                    embeddings.append(embedding)
                    segment_info.append({
                        'start': start_time,
                        'end': end_time,
                        'embedding': embedding
                    })

                except Exception as e:
                    print(f"Failed to process segment {i+1}: {e}")
                    continue

            if not embeddings:
                print("No valid embeddings extracted")
                return []

            if progress_callback:
                progress_callback("Clustering speakers...", 70)

            # Step 3: Cluster embeddings to identify speakers
            print(f"Clustering {len(embeddings)} embeddings...")
            embeddings_array = np.array(embeddings)

            # Determine number of speakers (adaptive)
            n_speakers = min(max_speakers, max(2, len(embeddings) // 3))

            # Check if clustering is available
            if not SKLEARN_AVAILABLE:
                print("scikit-learn not available, using simple speaker assignment")
                # Simple fallback: assign alternating speakers
                speaker_labels = [i % 2 for i in range(len(embeddings))]
            else:
                # Use Agglomerative Clustering (works well with speaker embeddings)
                clustering = AgglomerativeClustering(
                    n_clusters=n_speakers,
                    metric='cosine',
                    linkage='average'
                )
                speaker_labels = clustering.fit_predict(embeddings_array)

            if progress_callback:
                progress_callback("Finalizing speaker assignments...", 90)

            # Step 4: Create speaker segments
            speaker_segments = []
            for i, segment in enumerate(segment_info):
                speaker_label = f"Speaker_{speaker_labels[i]:02d}"
                speaker_segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'speaker': speaker_label
                })

            # Sort by start time
            speaker_segments.sort(key=lambda x: x['start'])

            if progress_callback:
                progress_callback("Speaker detection complete!", 100)

            unique_speakers = len(set([seg['speaker'] for seg in speaker_segments]))
            print(f"Identified {unique_speakers} unique speakers in {len(speaker_segments)} segments")

            return speaker_segments

        except Exception as e:
            print(f"Error during speaker detection: {e}")
            import traceback
            traceback.print_exc()
            return []

    def assign_speakers_to_chunks(self, speaker_segments, audio_chunks_info):
        """
        Assign speakers to transcription chunks
        Same interface as the pyannote version for compatibility
        """
        results = []

        for chunk in audio_chunks_info:
            chunk_start = chunk['start_time']
            chunk_end = chunk['end_time']
            chunk_transcript = chunk['transcript']

            # Find overlapping speaker segments
            overlapping_speakers = []
            for segment in speaker_segments:
                # Check if speaker segment overlaps with chunk
                if (segment['start'] < chunk_end and segment['end'] > chunk_start):
                    overlap_start = max(segment['start'], chunk_start)
                    overlap_end = min(segment['end'], chunk_end)
                    overlap_duration = overlap_end - overlap_start

                    if overlap_duration > 0:
                        overlapping_speakers.append({
                            'speaker': segment['speaker'],
                            'duration': overlap_duration
                        })

            # Determine dominant speaker (longest speaking time in chunk)
            if overlapping_speakers:
                dominant_speaker = max(overlapping_speakers, key=lambda x: x['duration'])['speaker']
            else:
                dominant_speaker = "Speaker_00"  # Default speaker

            results.append({
                'start_time': chunk_start,
                'end_time': chunk_end,
                'transcript': chunk_transcript,
                'speaker': dominant_speaker
            })

        return results

    def format_transcript_with_speakers(self, speaker_chunks):
        """
        Format transcript with speaker labels and line breaks
        Same interface as the pyannote version for compatibility
        """
        if not speaker_chunks:
            return ""

        formatted_parts = []
        current_speaker = None

        print(f"Formatting {len(speaker_chunks)} speaker chunks...")  # Debug

        for i, chunk in enumerate(speaker_chunks):
            speaker = chunk['speaker']
            transcript = chunk['transcript'].strip()

            if not transcript:
                continue

            print(f"Chunk {i}: Speaker={speaker}, Current={current_speaker}, Text='{transcript[:50]}...'")  # Debug

            # Add speaker label when speaker changes
            if speaker != current_speaker:
                # Add single line break between different speakers for readability
                if current_speaker is not None:  # Not the first speaker
                    formatted_parts.append(f"\n[{speaker}]: {transcript}")
                    print(f"  Adding NEW SPEAKER with line break: \\n[{speaker}]: {transcript[:30]}...")  # Debug
                else:  # First speaker
                    formatted_parts.append(f"[{speaker}]: {transcript}")
                    print(f"  Adding FIRST SPEAKER: [{speaker}]: {transcript[:30]}...")  # Debug
                current_speaker = speaker
            else:
                # Same speaker, continue transcript
                formatted_parts.append(f" {transcript}")
                print(f"  Adding SAME SPEAKER continuation: {transcript[:30]}...")  # Debug

        result = "".join(formatted_parts).strip()
        print(f"Final formatted transcript length: {len(result)}")
        print(f"First 200 chars of result: {repr(result[:200])}")  # Debug
        return result