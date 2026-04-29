import { Modal, ScrollView, View, TouchableOpacity, Text } from "react-native";
import { useState, useEffect } from "react";
import { X, Utensils, Stethoscope } from "lucide-react-native";

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
          <View className="flex-row justify-end px-4 pt-3">
            <TouchableOpacity onPress={handleClose} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
              <X size={22} color="#eea487" strokeWidth={2.25} />
            </TouchableOpacity>
          </View>

          <ScrollView className="px-5 pb-8" keyboardShouldPersistTaps="handled">
            {step === "select_type" && (
              <View className="items-center pt-4 gap-5 pb-6">
                <Text className="text-2xl font-bold font-ptserif mb-3 text-remetra-burgundy">
                  What Are You Logging?
                </Text>

                <TouchableOpacity
                  className="w-full flex-row items-center gap-4 border border-remetra-burgundy rounded-2xl p-5 bg-remetra-orange/10"
                  onPress={() => setStep("food")}
                >
                  <Utensils size={20} color="#5C2E14" strokeWidth={1.75} />
                  <Text className="text-lg font-semibold font-ptserif text-remetra-espresso">Food</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  className="w-full flex-row items-center gap-4 border border-remetra-burgundy rounded-2xl p-5 bg-remetra-orange/10"
                  onPress={() => setStep("symptom")}
                >
                  <Stethoscope size={20} color="#5C2E14" strokeWidth={1.75} />
                  <Text className="text-lg font-semibold font-ptserif text-remetra-espresso">Symptom</Text>
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