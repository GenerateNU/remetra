import { FoodLogEntry, FoodItem } from "../types/logs";
import { useBankStore } from "../store/bankStore";
import { Chips } from "./GenericChipComponent";

import { useState } from "react";
import  DateTimePicker from '@react-native-community/datetimepicker'
import { View, Text, TouchableOpacity, TextInput } from "react-native";

interface FoodLogFormProps {
  onSubmit: (entry: FoodLogEntry) => void;
  onBack: () => void;
}

export const FoodLogForm: React.FC<FoodLogFormProps> = ({ onSubmit, onBack }) => {
  const { foods, addCustomFood } = useBankStore();

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
    const foodId = isCustom
      ? addCustomFood(customName, customIngredients)
      : selectedFood?.id

    // this will never occur
    if (!foodId) {
      console.error("How the hell did this happen")
      return;
    }
    const entry: FoodLogEntry = {
      type: "food",
      foodId,
      name: isCustom ? customName : selectedFood?.name ?? "",
      ingredients: isCustom
        ? customIngredients
        : selectedFood?.ingredients ?? [],
      servings: parseFloat(servings) || 1,
      timestamp,
    };
    console.log('New food log: ', entry)
    onSubmit(entry);
  };

  const isValid = isCustom
    ? customName.trim().length > 0
    : selectedFood !== null;

  return (
    <View className="pb-10">
      <TouchableOpacity onPress={onBack}>
        <Text className="text-base text-blue-500 mb-4">← Back</Text>
      </TouchableOpacity>

      <Text className="text-2xl font-bold mb-3 text-neutral-900">
        Log Food
      </Text>

      {/* Search / Select */}
      {!selectedFood && !isCustom && (
        <>
          <TextInput
            className="border border-neutral-300 rounded-lg p-3 text-base bg-neutral-50 mb-2"
            placeholder="Search foods..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <View className="gap-1 mb-3">
            {filtered.map((food) => (
              <TouchableOpacity
                key={food.id}
                className="p-3.5 bg-neutral-50 rounded-lg border border-neutral-200"
                onPress={() => handleSelectFood(food)}
              >
                <Text className="text-base font-medium text-neutral-900">
                  {food.name}
                </Text>
                <Text className="text-xs text-neutral-400 mt-0.5">
                  {food.ingredients.join(", ")}
                </Text>
              </TouchableOpacity>
            ))}
            {searchQuery.trim().length > 0 && (
              <TouchableOpacity
                className="p-3.5 bg-neutral-50 rounded-lg border border-blue-500 border-dashed"
                onPress={handleSwitchToCustom}
              >
                <Text className="text-blue-500 font-medium text-base">
                  + Add "{searchQuery}" as custom food
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </>
      )}

      {/* Selected food summary */}
      {selectedFood && !isCustom && (
        <View className="bg-blue-50 p-3.5 rounded-xl border border-blue-500/25 mb-2">
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-neutral-900">
              {selectedFood.name}
            </Text>
            <TouchableOpacity
              onPress={() => {
                setSelectedFood(null);
                setSearchQuery("");
              }}
            >
              <Text className="text-blue-500 text-sm font-medium">Change</Text>
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
            className="border border-neutral-300 rounded-lg p-3 text-base bg-neutral-50 mb-2"
            placeholder="Food name"
            value={customName}
            onChangeText={setCustomName}
          />
          <Chips
            items={customIngredients}
            itemName="Ingredients"
            onAdd={(ing) => setCustomIngredients((prev) => [...prev, ing])}
            onRemove={(i) =>
              setCustomIngredients((prev) => prev.filter((_, idx) => idx !== i))
            }
          />
          <TouchableOpacity
            onPress={() => {
              setIsCustom(false);
              setSearchQuery("");
            }}
          >
            <Text className="text-blue-500 text-sm font-medium mt-2">
              Search bank instead
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Servings + Timestamp */}
      {(selectedFood || isCustom) && (
        <>
          <Text className="text-sm font-semibold text-neutral-600 mt-4 mb-1.5">
            Servings
          </Text>
          <TextInput
            className="border border-neutral-300 rounded-lg p-3 text-base bg-neutral-50 mb-2"
            keyboardType="numeric"
            value={servings}
            onChangeText={setServings}
            placeholder="1"
          />

          <Text className="text-sm font-semibold text-neutral-600 mt-4 mb-1.5">
            Time
          </Text>
          <TouchableOpacity
            className="border border-neutral-300 rounded-lg p-3 bg-neutral-50 mb-2"
            onPress={() => setShowDatePicker(true)}
          >
            <Text>{timestamp.toLocaleTimeString()}</Text>
          </TouchableOpacity>

            {showDatePicker && (
              <DateTimePicker
                value={timestamp}
                mode="time"
                onChange={(_, date) => {
                  setShowDatePicker(false);
                  if (date) setTimestamp(date);
                }}
              />
            )} 

          <TouchableOpacity
            className={`bg-blue-500 py-4 rounded-xl items-center mt-6 ${
              !isValid ? "opacity-40" : ""
            }`}
            onPress={handleSubmit}
            disabled={!isValid}
          >
            <Text className="text-white text-lg font-semibold">Log Food</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};