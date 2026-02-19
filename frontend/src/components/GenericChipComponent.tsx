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
  onAdd: (item: string) => void;
  onRemove: (index: number) => void;
}

export const Chips: React.FC<ChipsProps> = ({
  items,
  itemName,
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
      <TextInput
        className="border border-neutral-300 rounded-lg p-3 text-base bg-neutral-50 mb-2"
        placeholder={`Add ${itemName.toLowerCase()}...`}
        value={input}
        onChangeText={setInput}
        onSubmitEditing={handleSubmit}
        returnKeyType="done"
      />
    </View>
  );
};