import AsyncStorage from '@react-native-async-storage/async-storage';

export type Task = {
  id: string;
  title: string;
  done: boolean;
  createdAt: number;
};

const STORAGE_KEY = 'tasks.v1';

/**
 * Reads the saved tasks. Returns [] for a first launch, unreadable JSON, or
 * anything that does not match the expected shape — a corrupt value should
 * start the user fresh rather than crash them out of the app on launch.
 */
export async function loadTasks(): Promise<Task[]> {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    if (!raw) return [];

    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    return parsed.filter(isTask);
  } catch {
    return [];
  }
}

export async function saveTasks(tasks: Task[]): Promise<void> {
  try {
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  } catch {
    // A failed write loses this change but must not take the UI down; the
    // in-memory list stays authoritative for the rest of the session.
  }
}

function isTask(value: unknown): value is Task {
  if (typeof value !== 'object' || value === null) return false;
  const t = value as Record<string, unknown>;
  return (
    typeof t.id === 'string' &&
    typeof t.title === 'string' &&
    typeof t.done === 'boolean' &&
    typeof t.createdAt === 'number'
  );
}
