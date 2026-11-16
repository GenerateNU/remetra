import { useState } from 'react';
import { Pressable, TextInput, View } from 'react-native';
import { SparkleSendIcon } from './icons';

const COMPOSER_SHADOW = {
  shadowColor: '#63311F',
  shadowOffset: { width: 0, height: 8 },
  shadowOpacity: 0.08,
  shadowRadius: 12,
  elevation: 4,
};

export function Composer({
  placeholder,
  disabled,
  onSend,
}: {
  placeholder: string;
  disabled: boolean;
  onSend: (text: string) => void;
}) {
  const [value, setValue] = useState('');
  const canSend = value.trim().length > 0 && !disabled;

  const submit = () => {
    if (!canSend) return;
    onSend(value);
    setValue('');
  };

  return (
    <View
      className="flex-row items-center gap-2 rounded-full border border-remetra-chip-line bg-white p-2"
      style={COMPOSER_SHADOW}
    >
      <TextInput
        accessibilityLabel="Message Remetra"
        value={value}
        onChangeText={setValue}
        onSubmitEditing={submit}
        placeholder={placeholder}
        placeholderTextColor="#7a7068"
        returnKeyType="send"
        submitBehavior="submit"
        maxLength={1000}
        className="flex-1 px-3 font-figtree text-[16px] text-remetra-text-primary"
        style={{ height: 24, paddingVertical: 0 }}
      />
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Send"
        accessibilityState={{ disabled: !canSend }}
        disabled={!canSend}
        onPress={submit}
        className="rounded-full bg-remetra-primary p-3"
        style={({ pressed }) => ({ opacity: !canSend ? 0.6 : pressed ? 0.88 : 1 })}
      >
        <SparkleSendIcon width={20} height={20} />
      </Pressable>
    </View>
  );
}
