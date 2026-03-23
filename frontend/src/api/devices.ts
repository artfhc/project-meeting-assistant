import type { AudioDevice } from '../types'
import { apiFetch } from './client'

export function listAudioDevices(): Promise<AudioDevice[]> {
  return apiFetch<AudioDevice[]>('/devices/audio')
}
