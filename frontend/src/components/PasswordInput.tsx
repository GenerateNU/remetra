import { useState } from 'react';
import { Pressable, TextInput, View, type TextInputProps } from 'react-native';
import { Eye, EyeOff } from 'lucide-react-native';

type PasswordInputProps = Omit<TextInputProps, 'secureTextEntry'>;

// Password field with an eye button that toggles whether the text is visible.
export function PasswordInput({ className, ...props }: PasswordInputProps) {
  const [visible, setVisible] = useState(false);
  const Icon = visible ? EyeOff : Eye;

  return (
    <View className="justify-center mb-2">
      <TextInput
        {...props}
        secureTextEntry={!visible}
        autoCapitalize="none"
        autoCorrect={false}
        className={`${className ?? ''} pr-12`}
      />
      <Pressable
        onPress={() => setVisible(v => !v)}
        hitSlop={8}
        accessibilityRole="button"
        accessibilityLabel={visible ? 'Hide password' : 'Show password'}
        className="absolute right-3"
      >
        <Icon size={20} color="#B8624F" /* remetra-burgundy */ />
      </Pressable>
    </View>
  );
}
