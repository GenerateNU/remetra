import { Modal, ScrollView, View, TouchableOpacity, Text } from "react-native";
import { useState, useEffect } from "react";

import { LogEntry, ModalStep } from "../types/logs";
import { FoodLogForm } from "./FoodLogForm";
import { SymptomLogForm } from "./SymptomLogForm";

interface LogEntryModalProps {
  visible: boolean;
  onClose: () => void;
  onLogEntry: (entry: LogEntry) => void;
  initialStep?: ModalStep; 
}
const LogEntryModal: React.FC<LogEntryModalProps> = ({ visible, onClose, onLogEntry, initialStep }) => {
  const [step, setStep] = useState<ModalStep>(initialStep ?? "select_type");

  useEffect(() => {
    if (visible) {
      setStep(initialStep ?? "select_type");
    }
  }, [visible, initialStep]);

  const handleSubmit = (entry: LogEntry) => {
    onLogEntry(entry);
    handleClose();
  };

  

  const handleClose = () => {
    onClose();
    setTimeout(() => setStep(initialStep ?? "select_type"), 300);
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
              <Text className="text-xl p-1 font-ptserif text-remetra-accent">✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView className="px-5 pb-8" keyboardShouldPersistTaps="handled">
            {step === "select_type" && (
              <View className="items-center pt-4 gap-5 pb-6">
                <Text className="text-2xl font-bold font-ptserif mb-3 text-remetra-accent">
                  What are you logging?
                </Text>

                <TouchableOpacity
                  className="w-full flex-row items-center gap-4 border border-remetra-border rounded-2xl p-5"
                  onPress={() => setStep("food")}
                >
                  <Text className="text-3xl">🍽</Text>
                  <Text className="text-lg font-semibold font-ptserif text-remetra-accent">Food</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  className="w-full flex-row items-center gap-4 border border-remetra-border rounded-2xl p-5"
                  onPress={() => setStep("symptom")}
                >
                  <Text className="text-3xl">🩺</Text>
                  <Text className="text-lg font-semibold font-ptserif text-remetra-accent">Symptom</Text>
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