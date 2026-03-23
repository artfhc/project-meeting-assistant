import { create } from 'zustand'
import type { Job } from '../types'

interface JobStore {
  jobs: Record<string, Job>
  setJob: (job: Job) => void
  clearJob: (meetingId: string) => void
}

export const useJobStore = create<JobStore>((set) => ({
  jobs: {},

  setJob: (job) =>
    set((state) => ({
      jobs: { ...state.jobs, [job.meeting_id]: job },
    })),

  clearJob: (meetingId) =>
    set((state) => {
      const next = { ...state.jobs }
      delete next[meetingId]
      return { jobs: next }
    }),
}))
