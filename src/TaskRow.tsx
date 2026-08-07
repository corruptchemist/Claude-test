import { Pressable, StyleSheet, Text, View } from 'react-native';

import type { Task } from './storage';
import type { Theme } from './theme';

type Props = {
  task: Task;
  theme: Theme;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
};

export function TaskRow({ task, theme, onToggle, onDelete }: Props) {
  return (
    <View style={[styles.row, { backgroundColor: theme.card, borderColor: theme.border }]}>
      <Pressable
        style={styles.main}
        onPress={() => onToggle(task.id)}
        accessibilityRole="checkbox"
        accessibilityState={{ checked: task.done }}
        accessibilityLabel={task.title}
        hitSlop={8}
      >
        <View
          style={[
            styles.checkbox,
            { borderColor: task.done ? theme.accent : theme.placeholder },
            task.done && { backgroundColor: theme.accent },
          ]}
        >
          {task.done ? <Text style={styles.checkmark}>✓</Text> : null}
        </View>

        <Text
          style={[
            styles.title,
            { color: task.done ? theme.textMuted : theme.text },
            task.done && styles.titleDone,
          ]}
          numberOfLines={2}
        >
          {task.title}
        </Text>
      </Pressable>

      <Pressable
        onPress={() => onDelete(task.id)}
        accessibilityRole="button"
        accessibilityLabel={`Delete ${task.title}`}
        hitSlop={10}
        style={styles.deleteButton}
      >
        <Text style={[styles.deleteLabel, { color: theme.danger }]}>✕</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: StyleSheet.hairlineWidth,
    paddingLeft: 14,
    paddingRight: 6,
    marginBottom: 8,
  },
  main: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  checkmark: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
    lineHeight: 16,
  },
  title: {
    flex: 1,
    fontSize: 17,
  },
  titleDone: {
    textDecorationLine: 'line-through',
  },
  deleteButton: {
    paddingHorizontal: 12,
    paddingVertical: 14,
  },
  deleteLabel: {
    fontSize: 17,
    fontWeight: '600',
  },
});
