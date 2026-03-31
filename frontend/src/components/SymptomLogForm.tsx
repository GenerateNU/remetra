import { SymptomLogEntry, SymptomItem } from "../types/logs";
import { useBankStore } from "../store/bankStore";
import { symptomLogService } from "../api/symptom_log_service";
import { useAuthStore } from "../store/useAuthStore";

import { useState } from "react";
import DateTimePicker from "@react-native-community/datetimepicker";
import { View, Text, TouchableOpacity, TextInput } from "react-native";

interface SymptomLogFormProps {
  onSubmit: (entry: SymptomLogEntry) => void;
  onBack: () => void;
}

export const SymptomLogForm: React.FC<SymptomLogFormProps> = ({ onSubmit, onBack }) => {
  const username = useAuthStore((s) => s.user.name) ?? "";
  const { symptoms, addSymptom } = useBankStore();

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
  const [notes, setNotes] = useState("");

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

  const handleSubmit = async () => {
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
      ? await addSymptom(customName, customLocation, customSensation)
      : selectedSymptom?.id ?? null;

    if (!symptomId) {
      console.error("Could not resolve symptom ID for log entry");
      return;
    }

    try {
      await symptomLogService.createSymptomLog({
        symptom_id: symptomId,
        intensity,
        timestamp: timestamp.toISOString(),
        duration: showDuration ? parseFloat(durationMinutes) || undefined : undefined,
        notes: notes.trim() || undefined,
        username,
      });
    } catch (error) {
      console.error("Failed to create symptom log entry:", error);
      return;
    }

    const entry: SymptomLogEntry = {
      type: "symptom",
      symptomId: symptomId,
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
        <Text className="text-base font-ptserif text-[#eea487] mb-4">← Back</Text>
      </TouchableOpacity>

      <Text className="text-2xl font-bold font-ptserif mb-3 text-[#eea487]">
        Log Symptom
      </Text>

      {/* Search / Select */}
      {!selectedSymptom && !isCustom && (
        <>
          <TextInput
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 8, backgroundColor: '#fafafa' }}
            placeholder="Search symptoms..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <View className="gap-1 mb-3">
            {filtered.map((sy) => (
              <TouchableOpacity
                key={sy.id}
                style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 14, backgroundColor: '#fafafa' }}
                onPress={() => handleSelectSymptom(sy)}
              >
                <Text className="text-base font-medium text-neutral-900">{sy.name}</Text>
                <Text className="text-xs text-neutral-400 mt-0.5">
                  {sy.location} · {sy.sensation}
                </Text>
              </TouchableOpacity>
            ))}
            {searchQuery.trim().length > 0 && (
              <TouchableOpacity
                style={{ borderWidth: 1, borderColor: '#eea487', borderStyle: 'dashed', borderRadius: 8, padding: 14, backgroundColor: '#fafafa' }}
                onPress={handleSwitchToCustom}
              >
                <Text className="font-medium text-base font-ptserif text-[#eea487]">
                  + Add &apos;{searchQuery}&apos; as custom symptom
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </>
      )}

      {/* Selected symptom summary */}
      {selectedSymptom && !isCustom && (
        <View style={{ backgroundColor: '#fff5f0', borderWidth: 1, borderColor: '#eea487', borderRadius: 12, padding: 14, marginBottom: 8 }}>
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-neutral-900">{selectedSymptom.name}</Text>
            <TouchableOpacity onPress={() => { setSelectedSymptom(null); setSearchQuery(""); }}>
              <Text className="text-sm font-medium font-ptserif text-[#eea487]">Change</Text>
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
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 8, backgroundColor: '#fafafa' }}
            placeholder="Symptom name"
            value={customName}
            onChangeText={setCustomName}
          />
          <TextInput
            style={{ borderWidth: 1, borderColor: errors.location ? '#f87171' : '#ccc', borderRadius: 8, padding: 12, marginBottom: 2, backgroundColor: '#fafafa' }}
            placeholder="Location (e.g., stomach, head)"
            value={customLocation}
            onChangeText={(text) => { setCustomLocation(text); if (errors.location) clearError("location"); }}
          />
          {errors.location && (
            <Text className="text-red-500 text-xs mb-2">{errors.location}</Text>
          )}
          <TextInput
            style={{ borderWidth: 1, borderColor: errors.sensation ? '#f87171' : '#ccc', borderRadius: 8, padding: 12, marginBottom: 2, backgroundColor: '#fafafa' }}
            placeholder="Sensation (e.g., burning, throbbing)"
            value={customSensation}
            onChangeText={(text) => { setCustomSensation(text); if (errors.sensation) clearError("sensation"); }}
          />
          {errors.sensation && (
            <Text className="text-red-500 text-xs mb-2">{errors.sensation}</Text>
          )}
          <TouchableOpacity onPress={() => { setIsCustom(false); setSearchQuery(""); setErrors({}); }}>
            <Text className="text-sm font-medium font-ptserif text-[#eea487] mt-2">
              Search bank instead
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Intensity + Timestamp + Duration */}
      {(selectedSymptom || isCustom) && (
        <>
          <Text className="text-sm font-semibold font-ptserif text-[#eea487] mt-4 mb-1.5">
            Intensity: {intensity}/10
          </Text>
          <View className="flex-row justify-between gap-1 mb-2">
            {Array.from({ length: 10 }, (_, i) => i + 1).map((val) => (
              <TouchableOpacity
                key={val}
                style={{
                  width: 28, height: 28, borderRadius: 16,
                  alignItems: 'center', justifyContent: 'center',
                  backgroundColor: val <= intensity ? '#eea487' : '#e5e5e5',
                }}
                onPress={() => setIntensity(val)}
              >
                <Text style={{ fontSize: 12, fontWeight: '600', color: val <= intensity ? 'white' : '#a3a3a3' }}>
                  {val}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text className="text-sm font-semibold font-ptserif text-[#eea487] mt-4 mb-1.5">
            Time
          </Text>
          <TouchableOpacity
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, backgroundColor: '#fafafa', marginBottom: 8 }}
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
              <Text className="text-sm font-medium font-ptserif text-[#eea487] mt-2">
                + Add duration
              </Text>
            </TouchableOpacity>
          ) : (
            <View>
              <Text className="text-sm font-semibold font-ptserif text-[#eea487] mt-4 mb-1.5">
                Duration (minutes)
              </Text>
              <TextInput
                style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 8, backgroundColor: '#fafafa' }}
                keyboardType="numeric"
                value={durationMinutes}
                onChangeText={setDurationMinutes}
                placeholder="e.g., 30"
              />
            </View>
          )}
          <Text className="text-sm font-semibold font-ptserif text-[#eea487] mt-4 mb-1.5">
                Notes (optional)
              </Text>
              <TextInput
                style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 8, backgroundColor: '#fafafa' }}
                placeholder="Any additional notes..."
                value={notes}
                onChangeText={setNotes}
                multiline
              />
          <TouchableOpacity
            style={{
              borderWidth: 1, borderColor: '#ccc', borderRadius: 25,
              paddingVertical: 14, alignItems: 'center', marginTop: 24,
              opacity: isValid ? 1 : 0.4,
            }}
            onPress={handleSubmit}
            disabled={!isValid}
          >
            <Text className="text-lg font-ptserif text-[#eea487]">Log Symptom</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};