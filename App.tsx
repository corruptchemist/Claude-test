import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  useColorScheme,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';

import { TaskRow } from './src/TaskRow';
import { loadTasks, saveTasks, type Task } from './src/storage';
import { getTheme } from './src/theme';

export default function App() {
  return (
    <SafeAreaProvider>
      <TasksScreen />
    </SafeAreaProvider>
  );
}

function TasksScreen() {
  const scheme = useColorScheme();
  const theme = useMemo(() => getTheme(scheme), [scheme]);
  const insets = useSafeAreaInsets();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [draft, setDraft] = useState('');
  // Storage is only authoritative once the first read finishes. Writing before
  // then would persist the initial empty list over the user's real tasks.
  const [loaded, setLoaded] = useState(false);
  const inputRef = useRef<TextInput>(null);

  useEffect(() => {
    let active = true;
    loadTasks().then((saved) => {
      if (!active) return;
      setTasks(saved);
      setLoaded(true);
    });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (loaded) void saveTasks(tasks);
  }, [tasks, loaded]);

  const addTask = useCallback(() => {
    const title = draft.trim();
    if (!title) return;

    setTasks((current) => [
      {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        title,
        done: false,
        createdAt: Date.now(),
      },
      ...current,
    ]);
    setDraft('');
    inputRef.current?.focus();
  }, [draft]);

  const toggleTask = useCallback((id: string) => {
    setTasks((current) =>
      current.map((task) => (task.id === id ? { ...task, done: !task.done } : task)),
    );
  }, []);

  const deleteTask = useCallback((id: string) => {
    setTasks((current) => current.filter((task) => task.id !== id));
  }, []);

  const remaining = tasks.filter((task) => !task.done).length;
  const canAdd = draft.trim().length > 0;

  return (
    <View style={[styles.root, { backgroundColor: theme.background }]}>
      <StatusBar style={scheme === 'dark' ? 'light' : 'dark'} />

      <KeyboardAvoidingView
        style={styles.root}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
          <Text style={[styles.heading, { color: theme.text }]}>Tasks</Text>
          <Text style={[styles.subheading, { color: theme.textMuted }]}>
            {tasks.length === 0
              ? 'Nothing yet'
              : `${remaining} of ${tasks.length} remaining`}
          </Text>
        </View>

        <FlatList
          data={tasks}
          keyExtractor={(task) => task.id}
          renderItem={({ item }) => (
            <TaskRow task={item} theme={theme} onToggle={toggleTask} onDelete={deleteTask} />
          )}
          contentContainerStyle={[
            styles.listContent,
            tasks.length === 0 && styles.listContentEmpty,
          ]}
          keyboardDismissMode="interactive"
          keyboardShouldPersistTaps="handled"
          ListEmptyComponent={
            loaded ? (
              <View style={styles.empty}>
                <Text style={[styles.emptyTitle, { color: theme.text }]}>No tasks yet</Text>
                <Text style={[styles.emptyBody, { color: theme.textMuted }]}>
                  Add your first one below. Tap a task to mark it done.
                </Text>
              </View>
            ) : null
          }
        />

        <View
          style={[
            styles.composer,
            {
              backgroundColor: theme.card,
              borderTopColor: theme.border,
              paddingBottom: insets.bottom + 12,
            },
          ]}
        >
          <TextInput
            ref={inputRef}
            value={draft}
            onChangeText={setDraft}
            placeholder="Add a task"
            placeholderTextColor={theme.placeholder}
            style={[
              styles.input,
              { backgroundColor: theme.background, color: theme.text, borderColor: theme.border },
            ]}
            returnKeyType="done"
            onSubmitEditing={addTask}
            // Keeps the keyboard up for rapid entry of several tasks.
            blurOnSubmit={false}
            maxLength={200}
          />
          <Pressable
            onPress={addTask}
            disabled={!canAdd}
            accessibilityRole="button"
            accessibilityLabel="Add task"
            style={[
              styles.addButton,
              { backgroundColor: canAdd ? theme.accent : theme.border },
            ]}
          >
            <Text
              style={[styles.addLabel, { color: canAdd ? '#FFFFFF' : theme.textMuted }]}
            >
              Add
            </Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  heading: {
    fontSize: 34,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  subheading: {
    fontSize: 15,
    marginTop: 2,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingTop: 4,
    paddingBottom: 16,
  },
  listContentEmpty: {
    flexGrow: 1,
    justifyContent: 'center',
  },
  empty: {
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 6,
  },
  emptyBody: {
    fontSize: 15,
    textAlign: 'center',
    lineHeight: 21,
  },
  composer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingHorizontal: 16,
    paddingTop: 12,
    borderTopWidth: StyleSheet.hairlineWidth,
  },
  input: {
    flex: 1,
    height: 44,
    borderRadius: 10,
    borderWidth: StyleSheet.hairlineWidth,
    paddingHorizontal: 14,
    fontSize: 17,
  },
  addButton: {
    height: 44,
    paddingHorizontal: 18,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addLabel: {
    fontSize: 16,
    fontWeight: '600',
  },
});
