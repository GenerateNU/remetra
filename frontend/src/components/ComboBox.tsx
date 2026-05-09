import { useEffect, useRef, useState } from 'react';
import {
  Modal,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
} from 'react-native';

interface ComboBoxProps {
  value: string;
  onSelect: (value: string) => void;
  options: string[];
  placeholder?: string;
  allowCustom?: boolean;
}

export function ComboBox({
  value,
  onSelect,
  options,
  placeholder,
  allowCustom = true,
}: ComboBoxProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const inputRef = useRef<TextInput>(null);

  useEffect(() => {
    if (open) {
      setQuery(value || '');
    }
  }, [open, value]);

  const trimmed = query.trim();
  const filtered = options.filter((item) =>
    item.toLowerCase().includes(query.toLowerCase())
  );
  const exactMatch = options.some(
    (item) => item.toLowerCase() === trimmed.toLowerCase()
  );

  const close = () => setOpen(false);

  const handleSelect = (item: string) => {
    onSelect(item);
    setOpen(false);
  };

  const handleSubmit = () => {
    if (allowCustom && trimmed) {
      onSelect(trimmed);
      setOpen(false);
    }
  };

  return (
    <>
      <TouchableOpacity
        onPress={() => setOpen(true)}
        className="border border-remetra-border rounded-lg p-3 bg-remetra-surface"
        activeOpacity={0.7}
      >
        <Text className={value ? 'text-remetra-espresso' : 'text-remetra-muted'}>
          {value || placeholder || 'Select...'}
        </Text>
      </TouchableOpacity>

      <Modal
        visible={open}
        transparent
        animationType="fade"
        onRequestClose={close}
        onShow={() => inputRef.current?.focus()}
      >
        <Pressable
          onPress={close}
          className="flex-1 bg-black/50 justify-center items-center px-6"
        >
          <Pressable
            onPress={() => {}}
            className="bg-white rounded-2xl w-full p-4"
            style={{ maxHeight: '70%' }}
          >
            <TextInput
              ref={inputRef}
              value={query}
              placeholder={placeholder ?? 'Search...'}
              placeholderTextColor="#aaa"
              className="border border-remetra-border rounded-lg p-3 bg-remetra-surface text-remetra-espresso mb-3"
              onChangeText={setQuery}
              onSubmitEditing={handleSubmit}
              returnKeyType="done"
            />
            <ScrollView
              keyboardShouldPersistTaps="handled"
              style={{ maxHeight: 320 }}
            >
              {filtered.map((item) => (
                <TouchableOpacity
                  key={item}
                  onPress={() => handleSelect(item)}
                  className="px-3 py-3 border-b border-remetra-border/40"
                >
                  <Text className="text-remetra-espresso">{item}</Text>
                </TouchableOpacity>
              ))}
              {allowCustom && trimmed && !exactMatch ? (
                <TouchableOpacity onPress={handleSubmit} className="px-3 py-3">
                  <Text className="text-remetra-warm-brown">Add "{trimmed}"</Text>
                </TouchableOpacity>
              ) : null}
              {filtered.length === 0 && !(allowCustom && trimmed) ? (
                <Text className="text-remetra-muted text-center py-4">No matches</Text>
              ) : null}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>
    </>
  );
}
