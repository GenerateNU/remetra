import { SymptomLogEntry, SymptomItem } from "../types/logs";
import { useBankStore } from "../store/bankStore";
import { symptomLogService } from "../api/symptom_log_service";
import { useAuthStore } from "../store/useAuthStore";
import { useState } from "react";
import { View, Text, TouchableOpacity, TextInput } from "react-native";
import { Dropdown } from "react-native-element-dropdown";
import { LogDateTimePicker } from "./LogDateTimePicker";
import { sensationOptions, locationOptions } from "../types/symptomOptions";

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

  const [customLocation, setCustomLocation] = useState("");
  const [customSensation, setCustomSensation] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [intensity, setIntensity] = useState(5);
  const [timestamp, setTimestamp] = useState(new Date());
  const [showDuration, setShowDuration] = useState(false);
  const [durationMinutes, setDurationMinutes] = useState("");
  const [notes, setNotes] = useState("");

  const filtered = symptoms.filter((sy) =>
    sy.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelectSymptom = (symptom: SymptomItem) => {
    setSelectedSymptom(symptom);
    setSearchQuery(symptom.name);
  };

  const clearError = () => setErrors({});

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

    const derivedName = `${customSensation} — ${customLocation}`;
    const symptomId = isCustom
      ? await addSymptom(derivedName, customLocation, customSensation)
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
      name: isCustom ? derivedName : selectedSymptom?.name ?? "",
      location: isCustom ? customLocation : selectedSymptom?.location ?? "",
      sensation: isCustom ? customSensation : selectedSymptom?.sensation ?? "",
      intensity,
      timestamp,
      durationMinutes: showDuration ? parseFloat(durationMinutes) || null : null,
    };
    onSubmit(entry);
  };

  const isValid = isCustom
    ? customLocation.trim().length > 0 && customSensation.trim().length > 0
    : selectedSymptom !== null;

  return (
    <View className="pb-10">
      <TouchableOpacity onPress={() => {
        if (!selectedSymptom && !isCustom) {
          onBack()
        } else {
          setIsCustom(false); setSearchQuery(""); setSelectedSymptom(null);
          setCustomSensation(""); setCustomLocation("");
        }
          onBack
        }
      }>
        <Text className="text-base font-ptserif text-remetra-espresso mb-4">← Back</Text>
      </TouchableOpacity>

      <Text className="text-2xl font-bold font-ptserif mb-3 text-remetra-espresso">
        Log Symptom
      </Text>

      {/* Search / Select */}
      {!selectedSymptom && !isCustom && (
        <>
          <TextInput
            className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface"
            placeholder="Search symptoms..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <TouchableOpacity
            className="rounded-lg p-3.5 bg-remetra-burgundy mb-2 opacity-80"
            onPress={() => setIsCustom(true)}
            activeOpacity={0.6}
          >
            <Text className="font-medium text-base font-ptserif text-white">+ New Symptom</Text>
          </TouchableOpacity>
          <View className="gap-2 mb-3">
            {filtered.map((sy) => (
              <TouchableOpacity
                key={sy.id}
                className="border border-remetra-mauve/40 rounded-lg p-3.5 bg-remetra-surface/30"
                onPress={() => handleSelectSymptom(sy)}
              >
                <Text className="text-base font-medium text-remetra-espresso">{sy.sensation}</Text>
                <Text className="text-xs text-remetra-burgundy/80 mt-0.5">Location: {sy.location}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </>
      )}

      {/* Selected symptom summary */}
      {selectedSymptom && !isCustom && (
        <View className="bg-remetra-surface-accent border border-remetra-espresso/80 rounded-xl p-3.5 mb-2">
          <View className="flex-row justify-between items-start">
            <View>
              <Text className="text-lg font-semibold text-remetra-espresso">{selectedSymptom.sensation}</Text>
              <Text className="text-xs text-remetra-warm-brown mt-0.5">Location: {selectedSymptom.location}</Text>
            </View>
          </View>
        </View>
      )}

      {/* New symptom inline form */}
      {isCustom && (
        <View>
          {/* Dropdown is a third-party component that only accepts style, not className */}
          <Dropdown
            data={sensationOptions}
            search
            labelField="label"
            valueField="value"
            placeholder="Select a sensation..."
            searchPlaceholder="Type to search..."
            value={customSensation}
            onChange={item => { setCustomSensation(item.value); if (errors.sensation) clearError(); }}
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 8 }}
            placeholderStyle={{ color: '#aaa', fontSize: 14 }}
            selectedTextStyle={{ fontSize: 14, color: '#5C2E14' }}
            itemTextStyle={{ color: '#5C2E14'}}
          />
          {errors.sensation && (
            <Text className="text-red-400 text-xs mb-2">{errors.sensation}</Text>
          )}
          <Dropdown
            data={locationOptions}
            search
            labelField="label"
            valueField="value"
            placeholder="Select a location..."
            searchPlaceholder="Type to search..."
            value={customLocation}
            onChange={item => { setCustomLocation(item.value); if (errors.location) clearError(); }}
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8 }}
            placeholderStyle={{ color: '#aaa', fontSize: 14 }}
            selectedTextStyle={{ fontSize: 14, color: '#5C2E14' }}
            itemTextStyle={{ color: '#5C2E14'}}
          />
          {errors.location && (
            <Text className="text-red-400 text-xs mb-2">{errors.location}</Text>
          )}
        </View>
      )}

      {/* Intensity + Timestamp + Duration */}
      {(selectedSymptom || isCustom) && (
        <>
          <Text className="text-sm font-semibold font-ptserif text-remetra-warm-brown mt-4 mb-1.5">
            Intensity: {intensity}/10
          </Text>
          <View className="flex-row justify-between gap-1 mb-2">
            {Array.from({ length: 10 }, (_, i) => i + 1).map((val) => (
              <TouchableOpacity
                key={val}
                className={`w-7 h-7 rounded-2xl items-center justify-center ${
                  val <= intensity ? 'bg-remetra-accent' : 'bg-neutral-200'
                }`}
                onPress={() => setIntensity(val)}
              >
                <Text className={`text-xs font-semibold ${val <= intensity ? 'text-white' : 'text-neutral-500'}`}>
                  {val}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text className="text-sm font-ptserif text-remetra-espresso mb-1.5">
            Time
          </Text>
          <LogDateTimePicker
            value={timestamp}
            onChange={setTimestamp}
            accentColor="#b8624fc0" /* remetra-accent */
          />

          {!showDuration ? (
            <TouchableOpacity onPress={() => setShowDuration(true)}>
              <Text className="text-sm font-medium font-ptserif text-remetra-burgundy mt-2">
                + Add duration
              </Text>
            </TouchableOpacity>
          ) : (
            <View>
              <Text className="text-sm font-semibold font-ptserif text-remetra-warm-brown mt-4 mb-1.5">
                Duration (minutes)
              </Text>
              <TextInput
                className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface text-remetra-espresso"
                keyboardType="numeric"
                value={durationMinutes}
                onChangeText={setDurationMinutes}
                placeholder="e.g., 30"
              />
            </View>
          )}

          <Text className="text-sm font-semibold font-ptserif text-remetra-warm-brown mt-2 mb-1.5">
            Notes (optional)
          </Text>
          <TextInput
            className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface text-remetra-espresso"
            placeholder="Any additional notes..."
            value={notes}
            onChangeText={setNotes}
            multiline
          />

          <TouchableOpacity
            className="border bg-remetra-burgundy/80 border-remetra-burgundy rounded-full py-3.5 items-center mt-6"
            style={{ opacity: isValid ? 1 : 0.4 }}
            onPress={handleSubmit}
            disabled={!isValid}
          >
            <Text className="text-lg font-ptserif text-white">Log Symptom</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};
