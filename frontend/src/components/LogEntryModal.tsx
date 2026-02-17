
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
      animationType="fade"
      transparent={true}
      onRequestClose={handleClose}
    >
      {/* Dimmed backdrop — tap to dismiss */}
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
              <Text className="text-xl text-neutral-500 p-1">✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView
            className="px-5 pb-8"
            keyboardShouldPersistTaps="handled"
          >
            {step === "select_type" && (
              <View className="items-center pt-4 gap-5 pb-6">
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
              <FoodLogForm
                onSubmit={handleSubmit}
                onBack={() => setStep("select_type")}
              />
            )}

            {step === "symptom" && (
              <SymptomLogForm
                onSubmit={handleSubmit}
                onBack={() => setStep("select_type")}
              />
            )}
          </ScrollView>
        </View>
      </TouchableOpacity>
    </Modal>
  );
};

export default LogEntryModal;