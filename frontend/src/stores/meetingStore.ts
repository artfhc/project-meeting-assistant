import { create } from 'zustand'
import type { Meeting } from '../types'

interface MeetingStore {
  meetings: Meeting[]
  selectedMeetingId: string | null
  setMeetings: (meetings: Meeting[]) => void
  selectMeeting: (id: string | null) => void
  upsertMeeting: (meeting: Meeting) => void
  removeMeeting: (id: string) => void
}

export const useMeetingStore = create<MeetingStore>((set) => ({
  meetings: [],
  selectedMeetingId: null,

  setMeetings: (meetings) => set({ meetings }),

  selectMeeting: (id) => set({ selectedMeetingId: id }),

  upsertMeeting: (meeting) =>
    set((state) => {
      const index = state.meetings.findIndex((m) => m.id === meeting.id)
      if (index === -1) {
        return { meetings: [meeting, ...state.meetings] }
      }
      const next = [...state.meetings]
      next[index] = meeting
      return { meetings: next }
    }),

  removeMeeting: (id) =>
    set((state) => ({
      meetings: state.meetings.filter((m) => m.id !== id),
      selectedMeetingId:
        state.selectedMeetingId === id ? null : state.selectedMeetingId,
    })),
}))
