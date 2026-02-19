import { FoodLogEntry, FoodItem } from "../types/logs";
import { useBankStore } from "../store/bankStore";
import { Chips } from "./GenericChipComponent";

import { useState } from "react";
import DateTimePicker from "@react-native-community/datetimepicker";
import { View, Text, TouchableOpacity, TextInput } from "react-native";

interface FoodLogFormProps {
  onSubmit: (entry: FoodLogEntry) => void;
  onBack: () => void;
}

export const FoodLogForm: React.FC<FoodLogFormProps> = ({ onSubmit, onBack }) => {
  const { foods, addFood } = useBankStore();

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFood, setSelectedFood] = useState<FoodItem | null>(null);
  const [isCustom, setIsCustom] = useState(false);

  const [customName, setCustomName] = useState("");
  const [customIngredients, setCustomIngredients] = useState<string[]>([]);

  const [servings, setServings] = useState("1");
  const [timestamp, setTimestamp] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);

  const filtered = foods.filter((f) =>
    f.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelectFood = (food: FoodItem) => {
    setSelectedFood(food);
    setIsCustom(false);
    setSearchQuery(food.name);
  };

  const handleSwitchToCustom = () => {
    setSelectedFood(null);
    setIsCustom(true);
    setCustomName(searchQuery);
  };

  const handleSubmit = () => {
    const foodId = isCustom ? addFood(customName, customIngredients) : selectedFood?.id;

    if (!foodId) {
      console.error("How the hell did this happen");
      return;
    }

    const entry: FoodLogEntry = {
      type: "food",
      foodId,
      name: isCustom ? customName : selectedFood?.name ?? "",
      ingredients: isCustom ? customIngredients : selectedFood?.ingredients ?? [],
      servings: parseFloat(servings) || 1,
      timestamp,
    };
    onSubmit(entry);
  };

  const isValid = isCustom ? customName.trim().length > 0 : selectedFood !== null;

  const endOfDay = new Date();
  endOfDay.setHours(23, 59, 59, 999);

  return (
    <View className="pb-10">
      <TouchableOpacity onPress={onBack}>
        <Text className="text-base font-ptserif text-[#eea487] mb-4">← Back</Text>
      </TouchableOpacity>

      <Text className="text-2xl font-bold font-ptserif mb-3 text-[#eea487]">
        Log Food
      </Text>

      {/* Search / Select */}
      {!selectedFood && !isCustom && (
        <>
          <TextInput
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 8, backgroundColor: '#fafafa' }}
            placeholder="Search foods..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <View className="gap-1 mb-3">
            {filtered.map((food) => (
              <TouchableOpacity
                key={food.id}
                style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 14, backgroundColor: '#fafafa' }}
                onPress={() => handleSelectFood(food)}
              >
                <Text className="text-base font-medium text-neutral-900">{food.name}</Text>
                <Text className="text-xs text-neutral-400 mt-0.5">
                  {food.ingredients.join(", ")}
                </Text>
              </TouchableOpacity>
            ))}
            {searchQuery.trim().length > 0 && (
              <TouchableOpacity
                style={{ borderWidth: 1, borderColor: '#eea487', borderStyle: 'dashed', borderRadius: 8, padding: 14, backgroundColor: '#fafafa' }}
                onPress={handleSwitchToCustom}
              >
                <Text className="font-medium text-base font-ptserif text-[#eea487]">
                  + Add &apos;{searchQuery}&apos; as custom food
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </>
      )}

      {/* Selected food summary */}
      {selectedFood && !isCustom && (
        <View style={{ backgroundColor: '#fff5f0', borderWidth: 1, borderColor: '#eea487', borderRadius: 12, padding: 14, marginBottom: 8 }}>
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-neutral-900">{selectedFood.name}</Text>
            <TouchableOpacity onPress={() => { setSelectedFood(null); setSearchQuery(""); }}>
              <Text className="text-sm font-medium font-ptserif text-[#eea487]">Change</Text>
            </TouchableOpacity>
          </View>
          <Text className="text-xs text-neutral-400 mt-0.5">
            {selectedFood.ingredients.join(", ")}
          </Text>
        </View>
      )}

      {/* Custom food entry */}
      {isCustom && (
        <View>
          <TextInput
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 8, backgroundColor: '#fafafa' }}
            placeholder="Food name"
            value={customName}
            onChangeText={setCustomName}
          />
          <Chips
            items={customIngredients}
            itemName="Ingredients"
            onAdd={(ing) => setCustomIngredients((prev) => [...prev, ing])}
            onRemove={(i) => setCustomIngredients((prev) => prev.filter((_, idx) => idx !== i))}
          />
          <TouchableOpacity onPress={() => { setIsCustom(false); setSearchQuery(""); }}>
            <Text className="text-sm font-medium font-ptserif text-[#eea487] mt-2">
              Search bank instead
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Servings + Timestamp */}
      {(selectedFood || isCustom) && (
        <>
          <Text className="text-sm font-semibold font-ptserif text-[#eea487] mt-4 mb-1.5">
            Servings
          </Text>
          <TextInput
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 8, backgroundColor: '#fafafa' }}
            keyboardType="numeric"
            value={servings}
            onChangeText={setServings}
            placeholder="1"
          />

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

          <TouchableOpacity
            style={{
              borderWidth: 1,
              borderColor: '#ccc',
              borderRadius: 25,
              paddingVertical: 14,
              alignItems: 'center',
              marginTop: 24,
              opacity: isValid ? 1 : 0.4,
            }}
            onPress={handleSubmit}
            disabled={!isValid}
          >
            <Text className="text-lg font-ptserif text-[#eea487]">Log Food</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};