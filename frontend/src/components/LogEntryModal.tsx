import { Modal, ScrollView, View, TouchableOpacity, Text } from "react-native";
import { useState } from "react";

import { LogEntry, ModalStep } from "../types/logs";
import { FoodLogForm } from "./FoodLogForm";
import { SymptomLogForm } from "./SymptomLogForm";

interface LogEntryModalProps {
  visible: boolean;
  onClose: () => void;
  onLogEntry: (entry: LogEntry) => void;
}

const LogEntryModal: React.FC<LogEntryModalProps> = ({ visible, onClose, onLogEntry }) => {
  const [step, setStep] = useState<ModalStep>("select_type");

  const handleSubmit = (entry: LogEntry) => {
    onLogEntry(entry);
    handleClose();
  };

  const handleClose = () => {
    onClose();
    setTimeout(() => setStep("select_type"), 300);
  };

  return (
    <Modal
      visible={visible}
      animationType="fade"
      transparent={true}
      onRequestClose={handleClose}
    >
      <TouchableOpacity
        className="flex-1 bg-black/50 justify-center items-center px-5"
        activeOpacity={1}
        onPress={handleClose}
      >
        <View
          className="bg-white rounded-3xl max-h-[75%] w-full"
          onStartShouldSetResponder={() => true}
        >
          <View className="flex-row justify-end px-4">
            <TouchableOpacity onPress={handleClose}>
              <Text className="text-xl p-1 font-ptserif text-[#eea487]">✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView className="px-5 pb-8" keyboardShouldPersistTaps="handled">
            {step === "select_type" && (
              <View className="items-center pt-4 gap-5 pb-6">
                <Text className="text-2xl font-bold font-ptserif mb-3 text-[#eea487]">
                  What are you logging?
                </Text>

                <TouchableOpacity
                  style={{ width: '100%', flexDirection: 'row', alignItems: 'center', gap: 16, borderWidth: 1, borderColor: '#ccc', borderRadius: 16, padding: 20 }}
                  onPress={() => setStep("food")}
                >
                  <Text className="text-3xl">🍽</Text>
                  <Text className="text-lg font-semibold font-ptserif text-[#eea487]">Food</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={{ width: '100%', flexDirection: 'row', alignItems: 'center', gap: 16, borderWidth: 1, borderColor: '#ccc', borderRadius: 16, padding: 20 }}
                  onPress={() => setStep("symptom")}
                >
                  <Text className="text-3xl">🩺</Text>
                  <Text className="text-lg font-semibold font-ptserif text-[#eea487]">Symptom</Text>
                </TouchableOpacity>
              </View>
            )}

            {step === "food" && (
              <FoodLogForm 
              onSubmit={handleSubmit} 
              onBack={() => setStep("select_type")} 
              onCloseModal={handleClose} /> 
            )}

            {step === "symptom" && (
              <SymptomLogForm onSubmit={handleSubmit} onBack={() => setStep("select_type")} />
            )}
          </ScrollView>
        </View>
      </TouchableOpacity>
    </Modal>
  );
};

export default LogEntryModal;