import { create } from 'zustand'

interface RecordingStore {
  isRecording: boolean
  elapsedSeconds: number
  currentMeetingId: string | null
  setRecording: (recording: boolean) => void
  setCurrentMeeting: (id: string | null) => void
  tickElapsed: () => void
  resetElapsed: () => void
}

export const useRecordingStore = create<RecordingStore>((set) => ({
  isRecording: false,
  elapsedSeconds: 0,
  currentMeetingId: null,

  setRecording: (recording) => set({ isRecording: recording }),

  setCurrentMeeting: (id) => set({ currentMeetingId: id }),

  tickElapsed: () =>
    set((state) => ({ elapsedSeconds: state.elapsedSeconds + 1 })),

  resetElapsed: () => set({ elapsedSeconds: 0 }),
}))
