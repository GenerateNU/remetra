import { SymptomLogEntry, SymptomItem } from "../types/logs";
import { useBankStore } from "../store/bankStore";
import { symptomLogService } from "../api/symptom_log_service";
import { useAuthStore } from "../store/useAuthStore";
import { useState } from "react";
import { View, Text, TouchableOpacity, TextInput } from "react-native";
import { LogDateTimePicker } from "./LogDateTimePicker";
import { CustomItemButton } from "./CustomItemButton";

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
  const [showDuration, setShowDuration] = useState(false);
  const [durationMinutes, setDurationMinutes] = useState("");
  const [notes, setNotes] = useState("");

  const filtered = symptoms.filter((sy) =>
    sy.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
        <Text className="text-base font-ptserif text-remetra-accent mb-4">← Back</Text>
      </TouchableOpacity>

      <Text className="text-2xl font-bold font-ptserif mb-3 text-remetra-accent">
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
          <View className="gap-1 mb-3">
            {filtered.map((sy) => (
              <TouchableOpacity
                key={sy.id}
                className="border border-remetra-border rounded-lg p-3.5 bg-remetra-surface"
                onPress={() => handleSelectSymptom(sy)}
              >
                <Text className="text-base font-medium text-remetra-accent">{sy.name}</Text>
                <Text className="text-xs text-neutral-400 mt-0.5">
                  {sy.location} · {sy.sensation}
                </Text>
              </TouchableOpacity>
            ))}
            {searchQuery.trim().length > 0 && (
              <CustomItemButton
                label={`+ Add '${searchQuery}' as custom symptom`}
                onPress={handleSwitchToCustom}
              />
            )}
          </View>
        </>
      )}

      {/* Selected symptom summary */}
      {selectedSymptom && !isCustom && (
        <View className="bg-remetra-surface-accent border border-remetra-accent rounded-xl p-3.5 mb-2">
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-neutral-900">{selectedSymptom.name}</Text>
            <TouchableOpacity onPress={() => { setSelectedSymptom(null); setSearchQuery(""); }}>
              <Text className="text-sm font-medium font-ptserif text-remetra-accent">Change</Text>
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
            className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface"
            placeholder="Symptom name"
            value={customName}
            onChangeText={setCustomName}
          />
          <TextInput
            className={`border ${errors.location ? 'border-red-400' : 'border-remetra-border'} rounded-lg p-3 mb-0.5 bg-remetra-surface`}
            placeholder="Location (e.g., stomach, head)"
            value={customLocation}
            onChangeText={(text) => { setCustomLocation(text); if (errors.location) clearError(); }}
          />
          {errors.location && (
            <Text className="text-red-400 text-xs mb-2">{errors.location}</Text>
          )}
          <TextInput
            className={`border ${errors.sensation ? 'border-red-400' : 'border-remetra-border'} rounded-lg p-3 mb-0.5 bg-remetra-surface`}
            placeholder="Sensation (e.g., burning, throbbing)"
            value={customSensation}
            onChangeText={(text) => { setCustomSensation(text); if (errors.sensation) clearError(); }}
          />
          {errors.sensation && (
            <Text className="text-red-400 text-xs mb-2">{errors.sensation}</Text>
          )}
          <TouchableOpacity onPress={() => { setIsCustom(false); setSearchQuery(""); setErrors({}); }}>
            <Text className="text-sm font-medium font-ptserif text-remetra-accent mt-2">
              Search bank instead
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Intensity + Timestamp + Duration */}
      {(selectedSymptom || isCustom) && (
        <>
          <Text className="text-sm font-semibold font-ptserif text-remetra-accent mt-4 mb-1.5">
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
                <Text className={`text-xs font-semibold ${val <= intensity ? 'text-white' : 'text-neutral-400'}`}>
                  {val}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text className="text-sm font-semibold font-ptserif text-remetra-accent mt-4 mb-1.5">
            Time
          </Text>
          <LogDateTimePicker
            value={timestamp}
            onChange={setTimestamp}
            accentColor="#eea487" /* remetra-accent */
          />

          {!showDuration ? (
            <TouchableOpacity onPress={() => setShowDuration(true)}>
              <Text className="text-sm font-medium font-ptserif text-remetra-accent mt-2">
                + Add duration
              </Text>
            </TouchableOpacity>
          ) : (
            <View>
              <Text className="text-sm font-semibold font-ptserif text-remetra-accent mt-4 mb-1.5">
                Duration (minutes)
              </Text>
              <TextInput
                className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface"
                keyboardType="numeric"
                value={durationMinutes}
                onChangeText={setDurationMinutes}
                placeholder="e.g., 30"
              />
            </View>
          )}

          <Text className="text-sm font-semibold font-ptserif text-remetra-accent mt-4 mb-1.5">
            Notes (optional)
          </Text>
          <TextInput
            className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface"
            placeholder="Any additional notes..."
            value={notes}
            onChangeText={setNotes}
            multiline
          />

          <TouchableOpacity
            className="border border-remetra-border rounded-full py-3.5 items-center mt-6"
            style={{ opacity: isValid ? 1 : 0.4 }}
            onPress={handleSubmit}
            disabled={!isValid}
          >
            <Text className="text-lg font-ptserif text-remetra-accent">Log Symptom</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};
