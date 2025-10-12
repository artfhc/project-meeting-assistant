# Fast Speaker Recognition Setup Guide

This guide explains how to enable **fast speaker identification** using Resemblyzer in the Meeting Assistant app.

## 🚀 **Why Resemblyzer?**

| Feature | pyannote.audio | **Resemblyzer** |
|---------|---------------|----------------|
| **Speed (21min audio)** | 15-45 minutes | **3-8 minutes** |
| **Setup complexity** | Complex (tokens, licenses) | **Simple** |
| **Account required** | Yes (Hugging Face) | **No** |
| **Works offline** | After setup | **Yes** |
| **Accuracy** | 95%+ | **85-90%** |

## 📦 **Installation**

```bash
pip install resemblyzer>=0.1.1 scikit-learn>=1.0.0 webrtcvad>=2.0.10
```

## ⚙️ **Setup Steps**

### 1. Enable Speaker Detection

Add to your `.env` file:

```env
ENABLE_SPEAKER_DIARIZATION=true
```

### 2. That's it! 🎉

**No additional setup required!** The app will:
- ✅ Download Resemblyzer models automatically (one-time, ~50MB)
- ✅ Work completely offline
- ✅ Process speaker detection **much faster**

## 🎯 **How It Works**

### **Processing Steps:**
1. **Voice Activity Detection** (10%) - Find speech vs silence
2. **Speaker Embeddings** (30-70%) - Extract voice "fingerprints"
3. **Speaker Clustering** (70-90%) - Group similar voices
4. **Assignment** (90-100%) - Assign speakers to transcript

### **Expected Timeline:**
| Audio Length | Processing Time |
|-------------|----------------|
| 30 seconds | 15-30 seconds |
| 5 minutes | 1-2 minutes |
| **21 minutes** | **3-8 minutes** |
| 1 hour | 8-15 minutes |

## 📊 **Output Format**

### **With Speaker Detection:**
```
[Speaker_00]: Hello everyone, let's start the meeting
[Speaker_01]: Thanks for joining, I have the project updates
[Speaker_00]: Great, please go ahead with the updates
[Speaker_01]: So far we've completed the database migration
```

### **Without Speaker Detection:**
```
Hello everyone, let's start the meeting. Thanks for joining, I have the project updates. Great, please go ahead with the updates. So far we've completed the database migration.
```

## 🔧 **Configuration Options**

### **Disable for Faster Processing:**
```env
ENABLE_SPEAKER_DIARIZATION=false
```

### **Processing Progress:**
- 0-5%: Audio loading
- 5-20%: **Fast speaker detection** ⭐
- 20-25%: Audio processing
- 25-90%: Transcription
- 90-100%: Finalization

## 🛠 **Troubleshooting**

### **"No module named 'resemblyzer'"**
```bash
pip install resemblyzer>=0.1.1
```

### **"No module named 'webrtcvad'"**
```bash
pip install webrtcvad>=2.0.10
```

### **Slow Performance**
- Speaker detection scales with audio length
- For very long files (>1 hour), consider disabling
- Processing time is still much faster than alternatives

### **Low Accuracy**
- Resemblyzer works best with clear, distinct voices
- Background noise can affect clustering
- Manual speaker correction may be needed for complex audio

## 🔄 **Fallback Behavior**

If speaker detection fails:
- ✅ **Transcription continues normally**
- ✅ **No speaker labels** (plain transcript)
- ✅ **Error messages in console**
- ✅ **App remains functional**

## 📈 **Performance Tips**

### **Best Results:**
- Clear audio quality
- Distinct speaker voices
- Minimal background noise
- 2-6 speakers (optimal)

### **Speed Optimization:**
- Use shorter audio files when possible
- Disable speaker detection for quick transcription-only
- Consider splitting very long recordings

## 🎉 **Ready to Use!**

Once you add `ENABLE_SPEAKER_DIARIZATION=true` to your `.env` file, the app will automatically:

1. **Load Resemblyzer models** (first run only)
2. **Process speaker detection** in 3-8 minutes for typical meetings
3. **Generate speaker-labeled transcripts**
4. **Create better meeting summaries** with speaker attribution

Enjoy fast, offline speaker recognition! 🚀