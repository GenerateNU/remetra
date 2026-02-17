
import { Modal, ScrollView, View, TouchableOpacity, Text } from "react-native";
import { useState } from "react";

import { LogEntry, ModalStep } from "../types/logs";

interface LogEntryModalProps {
  visible: boolean;
  onClose: () => void;
  onLogEntry: (entry: LogEntry) => void;
}

const LogEntryModal: React.FC<LogEntryModalProps> = ({
  visible,
  onClose,
  onLogEntry,
}) => {
  const [step, setStep] = useState<ModalStep>("select_type");

  const handleSubmit = (entry: LogEntry) => {
    onLogEntry(entry);
    handleClose();
  };

  const handleClose = () => {
    setStep("select_type");
    onClose();
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={handleClose}
    >
      <View className="flex-1 bg-white">
        <View className="flex-row justify-end p-4 pt-5">
          <TouchableOpacity onPress={handleClose}>
            <Text className="text-xl text-neutral-500 p-1">✕</Text>
          </TouchableOpacity>
        </View>

        <ScrollView
          className="flex-1 px-5"
          keyboardShouldPersistTaps="handled"
        >
          {step === "select_type" && (
            <View className="items-center pt-10 gap-5">
              <Text className="text-2xl font-bold mb-3 text-neutral-900">
                What are you logging?
              </Text>

              <TouchableOpacity
                className="w-full flex-row items-center gap-4 bg-neutral-100 p-5 rounded-2xl"
                onPress={() => setStep("food")}
              >
                <Text className="text-3xl">🍽</Text>
                <Text className="text-lg font-semibold text-neutral-900">
                  Food
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                className="w-full flex-row items-center gap-4 bg-neutral-100 p-5 rounded-2xl"
                onPress={() => setStep("symptom")}
              >
                <Text className="text-3xl">🩺</Text>
                <Text className="text-lg font-semibold text-neutral-900">
                  Symptom
                </Text>
              </TouchableOpacity>
            </View>
          )}

          {step === "food" && (
            <Text>Food log form</Text>
            // <FoodLogForm
            //   onSubmit={handleSubmit}
            //   onBack={() => setStep("select_type")}
            // />
          )}

          {step === "symptom" && (
            <Text>Symptom log form</Text>
            // <SymptomLogForm
            //   onSubmit={handleSubmit}
            //   onBack={() => setStep("select_type")}
            // />
          )}
        </ScrollView>
      </View>
    </Modal>
  );
};

export default LogEntryModal;