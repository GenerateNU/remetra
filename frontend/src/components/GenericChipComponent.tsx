import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
} from "react-native";
import { X } from "lucide-react-native";

interface ChipsProps {
  items: string[];
  itemName: string;
  placeholder?: string;
  onAdd: (item: string) => void;
  onRemove: (index: number) => void;
  chipClassName?: string;
  chipTextClassName?: string;
  removeIconColor?: string;
}

export const Chips: React.FC<ChipsProps> = ({
  items,
  itemName,
  placeholder,
  onAdd,
  onRemove,
  chipClassName = "bg-neutral-200",
  chipTextClassName = "text-neutral-700",
  removeIconColor = "#737373"
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
            className={`flex-row items-center rounded-full py-1.5 px-3 gap-1.5 ${chipClassName}`}
          >
            <Text className={`text-sm ${chipTextClassName}`}>{item}</Text>
            <TouchableOpacity onPress={() => onRemove(i)} hitSlop={{ top: 6, bottom: 6, left: 6, right: 6 }}>
              <X size={14} color={removeIconColor} strokeWidth={2.5} />
            </TouchableOpacity>
          </View>
        ))}
      </View>
      <View className="flex-row items-center gap-2">
        <TextInput
          className="flex-1 border border-neutral-300 bg-remetra-surface rounded-lg p-3 text-sm text-remetra-espresso"
          placeholder={placeholder ?? `Add ${itemName.toLowerCase()}...`}
          placeholderTextColor= "#aaa"
          value={input}
          onChangeText={setInput}
          onSubmitEditing={handleSubmit}
          returnKeyType="done"
          style={{ lineHeight: 16}}
          submitBehavior="submit"
        />
      </View>
    </View>
  );
};