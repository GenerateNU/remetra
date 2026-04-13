import React from 'react';
import { TouchableOpacity, Text } from 'react-native';

interface CustomItemButtonProps {
  label: string;
  onPress: () => void;
}

export function CustomItemButton({ label, onPress }: CustomItemButtonProps) {
  return (
    <TouchableOpacity
      className="border border-dashed border-remetra-accent rounded-lg p-3.5 bg-remetra-surface"
      onPress={onPress}
    >
      <Text className="font-medium text-base font-ptserif text-remetra-accent">{label}</Text>
    </TouchableOpacity>
  );
}
