import React from 'react';
import { Modal, View, Text, TouchableOpacity } from 'react-native';

interface BaseAddModalProps {
  visible: boolean;
  onClose: () => void;
  onAdd: () => void;
  addLabel: string;
  error?: string;
  children: React.ReactNode;
}

export function BaseAddModal({ visible, onClose, onAdd, addLabel, error, children }: BaseAddModalProps) {
  return (
    <Modal visible={visible} transparent animationType="fade">
      <View className="flex-1 bg-black/50 justify-center items-center">
        <View className="bg-white rounded-[20px] p-8 w-4/5">
          {children}
          {error ? <Text className="text-remetra-rose text-sm mt-2 mb-1">{error}</Text> : null}
          <View className="mt-5 gap-3">
            <TouchableOpacity
              onPress={onAdd}
              className="bg-remetra-burgundy rounded-full py-3.5 items-center"
            >
              <Text className="text-base font-ptserif text-white">{addLabel}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={onClose} className="items-center py-1">
              <Text className="text-sm font-ptserif text-remetra-warm-brown">Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}
