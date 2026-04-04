import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
} from "react-native";

interface ChipsProps {
  items: string[];
  itemName: string;
  placeholder?: string;
  onAdd: (item: string) => void;
  onRemove: (index: number) => void;
}

export const Chips: React.FC<ChipsProps> = ({
  items,
  itemName,
  placeholder,
  onAdd,
  onRemove,
}) => {
  const [input, setInput] = useState("");

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (trimmed.length === 0) return;
    onAdd(trimmed);
    setInput("");
  };

  return (
    <View>
      <View className="flex-row flex-wrap gap-2 mb-2">
        {items.map((item, i) => (
          <View
            key={`${item}-${i}`}
            className="flex-row items-center bg-neutral-200 rounded-full py-1.5 px-3 gap-1.5"
          >
            <Text className="text-sm text-neutral-700">{item}</Text>
            <TouchableOpacity onPress={() => onRemove(i)}>
              <Text className="text-sm text-neutral-500 font-semibold">✕</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
        <TextInput
          style={{ flex: 1, borderWidth: 1, borderColor: '#d4d4d4', borderRadius: 8, padding: 10, fontSize: 13, backgroundColor: '#fafafa' }}
          placeholder={placeholder ?? `Add ${itemName.toLowerCase()}...`}
          value={input}
          onChangeText={setInput}
          onSubmitEditing={handleSubmit}
          returnKeyType="done"
        />
        <TouchableOpacity
          onPress={handleSubmit}
          style={{ backgroundColor: '#eea487', borderRadius: 8, padding: 10 }}
        >
          <Text style={{ color: 'white', fontWeight: '600', fontSize: 13 }}>Add</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};