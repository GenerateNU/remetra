import { useState, useRef } from 'react';
import { View, TextInput, TouchableOpacity, Text, ScrollView } from 'react-native';

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
  const [query, setQuery] = useState(value || '');
  const [open, setOpen] = useState(false);
  const inputRef = useRef<TextInput>(null);

  const filtered = options.filter((item) =>
    item.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (item: string) => {
    setQuery(item);
    onSelect(item);
    setOpen(false);
    inputRef.current?.blur();
  };

  const handleSubmit = () => {
    if (allowCustom && query.trim()) {
      onSelect(query.trim());
      setOpen(false);
      inputRef.current?.blur();
    }
  };

  return (
    <View style={{ zIndex: open ? 1000 : 1, elevation: open ? 1000 : 1 }}>
      <TextInput
        ref={inputRef}
        value={query}
        placeholder={placeholder}
        placeholderTextColor="#aaa"
        className="border border-remetra-border rounded-lg p-3 bg-remetra-surface text-remetra-espresso"
        onChangeText={(text) => {
          setQuery(text);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 100)}
        onSubmitEditing={handleSubmit}
        returnKeyType="done"
      />
      {open && (
        <View
          className="bg-white border border-remetra-border rounded-lg"
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            marginTop: 4,
            maxHeight: 200,
            zIndex: 20,
          }}
        >
          <ScrollView keyboardShouldPersistTaps="handled" nestedScrollEnabled>
            {filtered.map((item) => (
              <TouchableOpacity
                key={item}
                onPress={() => handleSelect(item)}
                className="px-3 py-3"
              >
                <Text className="text-remetra-espresso">{item}</Text>
              </TouchableOpacity>
            ))}
            {filtered.length === 0 && allowCustom && query.trim() ? (
              <TouchableOpacity onPress={handleSubmit} className="px-3 py-3">
                <Text className="text-remetra-warm-brown">Add "{query.trim()}"</Text>
              </TouchableOpacity>
            ) : null}
          </ScrollView>
        </View>
      )}
    </View>
  );
}
