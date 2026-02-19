import { SymptomLogEntry, SymptomItem } from "../types/logs";
import { useBankStore } from "../store/bankStore";

import { useState } from "react";
import  DateTimePicker from '@react-native-community/datetimepicker'
import { View, Text, TouchableOpacity, TextInput } from "react-native";

interface SymptomLogFormProps {
  onSubmit: (entry: SymptomLogEntry) => void;
  onBack: () => void;
}

export const SymptomLogForm: React.FC<SymptomLogFormProps> = ({
  onSubmit,
  onBack,
}) => {
  const { symptoms, addCustomSymptom } = useBankStore();

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSymptom, setSelectedSymptom] = useState<SymptomItem | null>(null);
  const [isCustom, setIsCustom] = useState(false);

  const [customName, setCustomName] = useState("");
  const [customLocation, setCustomLocation] = useState("");
  const [customSensation, setCustomSensation] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [intensity, setIntensity] = useState(5);
  const [timestamp, setTimestamp] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showDuration, setShowDuration] = useState(false);
  const [durationMinutes, setDurationMinutes] = useState("");

  const filtered = symptoms.filter((sy) =>
    sy.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const endOfDay = new Date();
  endOfDay.setHours(23, 59, 59, 999);

  const handleSelectSymptom = (symptom: SymptomItem) => {
    setSelectedSymptom(symptom);
    setIsCustom(false);
    setSearchQuery(symptom.name);
  };

  const handleSwitchToCustom = () => {
    setSelectedSymptom(null);
    setIsCustom(true);
    setCustomName(searchQuery);
  };

  const clearError = (field: string) =>
    setErrors({});

  const handleSubmit = () => {
    if (isCustom) {
      const newErrors: Record<string, string> = {};
      if (!customLocation.trim()) newErrors.location = "Location is required.";
      if (!customSensation.trim()) newErrors.sensation = "Sensation is required.";
      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        return;
      }
    }

    setErrors({});

    const symptomId = isCustom
      ? addCustomSymptom(customName, customLocation, customSensation)
      : selectedSymptom?.id ?? null;

    if (!symptomId) {
      console.error("How the hell did this happen");
      return;
    }

    const entry: SymptomLogEntry = {
      type: "symptom",
      symptomId,
      name: isCustom ? customName : selectedSymptom?.name ?? "",
      location: isCustom ? customLocation : selectedSymptom?.location ?? "",
      sensation: isCustom ? customSensation : selectedSymptom?.sensation ?? "",
      intensity,
      timestamp,
      durationMinutes: showDuration ? parseFloat(durationMinutes) || null : null,
    };
    onSubmit(entry);
  };

  const isValid = isCustom ? customName.trim().length > 0 : selectedSymptom !== null;

  return (
    <View className="pb-10">
      <TouchableOpacity onPress={onBack}>
        <Text className="text-base text-blue-500 mb-4">← Back</Text>
      </TouchableOpacity>

      <Text className="text-2xl font-bold mb-3 text-neutral-900">
        Log Symptom
      </Text>

      {/* Search / Select */}
      {!selectedSymptom && !isCustom && (
        <>
          <TextInput
            className="border border-neutral-300 rounded-lg p-3 text-base bg-neutral-50 mb-2"
            placeholder="Search symptoms..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <View className="gap-1 mb-3">
            {filtered.map((sy) => (
              <TouchableOpacity
                key={sy.id}
                className="p-3.5 bg-neutral-50 rounded-lg border border-neutral-200"
                onPress={() => handleSelectSymptom(sy)}
              >
                <Text className="text-base font-medium text-neutral-900">
                  {sy.name}
                </Text>
                <Text className="text-xs text-neutral-400 mt-0.5">
                  {sy.location} · {sy.sensation}
                </Text>
              </TouchableOpacity>
            ))}
            {searchQuery.trim().length > 0 && (
              <TouchableOpacity
                className="p-3.5 bg-neutral-50 rounded-lg border border-blue-500 border-dashed"
                onPress={handleSwitchToCustom}
              >
                <Text className="text-blue-500 font-medium text-base">
                  + Add &lsquo;{searchQuery}&rsquo; as custom symptom
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </>
      )}

      {/* Selected symptom summary */}
      {selectedSymptom && !isCustom && (
        <View className="bg-blue-50 p-3.5 rounded-xl border border-blue-500/25 mb-2">
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-neutral-900">
              {selectedSymptom.name}
            </Text>
            <TouchableOpacity
              onPress={() => {
                setSelectedSymptom(null);
                setSearchQuery("");
              }}
            >
              <Text className="text-blue-500 text-sm font-medium">Change</Text>
            </TouchableOpacity>
          </View>
          <Text className="text-xs text-neutral-400 mt-0.5">
            {selectedSymptom.location} · {selectedSymptom.sensation}
          </Text>
        </View>
      )}

      {/* Custom symptom entry */}
      {isCustom && (
        <View>
          <TextInput
            className="border border-neutral-300 rounded-lg p-3 text-base bg-neutral-50 mb-2"
            placeholder="Symptom name"
            value={customName}
            onChangeText={setCustomName}
          />

          <TextInput
            className={`border rounded-lg p-3 text-base bg-neutral-50 mb-0.5 ${
              errors.location ? "border-red-400" : "border-neutral-300"
            }`}
            placeholder="Location (e.g., stomach, head)"
            value={customLocation}
            onChangeText={(text) => {
              setCustomLocation(text);
              if (errors.location) clearError("location");
            }}
          />
          {errors.location && (
            <Text className="text-red-500 text-xs mb-2">{errors.location}</Text>
          )}

          <TextInput
            className={`border rounded-lg p-3 text-base bg-neutral-50 mb-0.5 ${
              errors.sensation ? "border-red-400" : "border-neutral-300"
            }`}
            placeholder="Sensation (e.g., burning, throbbing)"
            value={customSensation}
            onChangeText={(text) => {
              setCustomSensation(text);
              if (errors.sensation) clearError("sensation");
            }}
          />
          {errors.sensation && (
            <Text className="text-red-500 text-xs mb-2">{errors.sensation}</Text>
          )}

          <TouchableOpacity
            onPress={() => {
              setIsCustom(false);
              setSearchQuery("");
              setErrors({});
            }}
          >
            <Text className="text-blue-500 text-sm font-medium mt-2">
              Search bank instead
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Intensity + Timestamp + Duration */}
      {(selectedSymptom || isCustom) && (
        <>
          <Text className="text-sm font-semibold text-neutral-600 mt-4 mb-1.5">
            Intensity: {intensity}/10
          </Text>
          <View className="flex-row justify-between gap-1 mb-2">
            {Array.from({ length: 10 }, (_, i) => i + 1).map((val) => (
              <TouchableOpacity
                key={val}
                className={`w-8 h-8 rounded-full items-center justify-center ${
                  val <= intensity ? "bg-blue-500" : "bg-neutral-200"
                }`}
                onPress={() => setIntensity(val)}
              >
                <Text
                  className={`text-xs font-semibold ${
                    val <= intensity ? "text-white" : "text-neutral-400"
                  }`}
                >
                  {val}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text className="text-sm font-semibold text-neutral-600 mt-4 mb-1.5">
            Time
          </Text>
          <TouchableOpacity
            className="border border-neutral-300 rounded-lg p-3 bg-neutral-50 mb-2"
            onPress={() => setShowDatePicker(true)}
          >
            <Text>
              {timestamp.toLocaleDateString()}{" "}
              {timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </Text>
          </TouchableOpacity>

          {showDatePicker && (
            <DateTimePicker
              value={timestamp}
              mode="datetime"
              display="spinner"
              maximumDate={endOfDay}
              onChange={(_, date) => {
                setShowDatePicker(false);
                if (date) setTimestamp(date);
              }}
            />
          )}

          {!showDuration ? (
            <TouchableOpacity onPress={() => setShowDuration(true)}>
              <Text className="text-blue-500 text-sm font-medium mt-2">
                + Add duration
              </Text>
            </TouchableOpacity>
          ) : (
            <View>
              <Text className="text-sm font-semibold text-neutral-600 mt-4 mb-1.5">
                Duration (minutes)
              </Text>
              <TextInput
                className="border border-neutral-300 rounded-lg p-3 text-base bg-neutral-50 mb-2"
                keyboardType="numeric"
                value={durationMinutes}
                onChangeText={setDurationMinutes}
                placeholder="e.g., 30"
              />
            </View>
          )}

          <TouchableOpacity
            className={`bg-blue-500 py-4 rounded-xl items-center mt-6 ${
              !isValid ? "opacity-40" : ""
            }`}
            onPress={handleSubmit}
            disabled={!isValid}
          >
            <Text className="text-white text-lg font-semibold">Log Symptom</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};