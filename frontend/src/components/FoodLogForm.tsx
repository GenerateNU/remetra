import { FoodLogEntry, FoodItem } from "../types/logs";
import { useBankStore } from "../store/bankStore";
import { Chips } from "./GenericChipComponent";
import { foodLogService } from "../api/food_log_service";
import { useAuthStore } from "../store/useAuthStore";
import { useNavigation } from '@react-navigation/native';
import { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, TextInput } from "react-native";
import { LogDateTimePicker } from "./LogDateTimePicker";
import { CustomItemButton } from "./CustomItemButton";

interface FoodLogFormProps {
  onSubmit: (entry: FoodLogEntry) => void;
  onBack: () => void;
  onCloseModal: () => void;
}

export const FoodLogForm: React.FC<FoodLogFormProps> = ({ onSubmit, onBack, onCloseModal }) => {
  const username = useAuthStore((s) => s.user.name) ?? "";
  const { foods, addFood } = useBankStore();
  const navigation = useNavigation<any>();

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFood, setSelectedFood] = useState<FoodItem | null>(null);
  const [isCustom, setIsCustom] = useState(false);

  const [customName, setCustomName] = useState("");
  const [customIngredients, setCustomIngredients] = useState<string[]>([]);
  const { scannedFood, setScannedFood } = useBankStore();

  useEffect(() => {
    if (scannedFood) {
      setCustomName(scannedFood.name);
      setCustomIngredients(scannedFood.ingredients);
      setIsCustom(true);
      setScannedFood(null);
    }
  }, []);

  const [servings, setServings] = useState("1");
  const [timestamp, setTimestamp] = useState(new Date());
  const [notes, setNotes] = useState("");

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

  const handleSubmit = async () => {
    const foodId = isCustom
      ? await addFood(customName, customIngredients)
      : selectedFood?.id;

    if (!foodId) {
      console.error("Could not resolve food ID for log entry");
      return;
    }

    try {
      await foodLogService.createFoodLog({
        food_id: foodId,
        quantity: `${servings} serving(s)`,
        timestamp: timestamp.toISOString(),
        notes: notes.trim() || undefined,
        username,
      });
    } catch (error) {
      console.error("Failed to create food log entry:", error);
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

  return (
    <View className="pb-10">
      <TouchableOpacity onPress={onBack}>
        <Text className="text-base font-ptserif text-remetra-accent mb-4">← Back</Text>
      </TouchableOpacity>

      <Text className="text-2xl font-bold font-ptserif mb-3 text-remetra-accent">
        Log Food
      </Text>

      {/* Search / Select */}
      {!selectedFood && !isCustom && (
        <>
          <TextInput
            className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface"
            placeholder="Search foods..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <View className="gap-1 mb-3">
            {filtered.map((food) => (
              <TouchableOpacity
                key={food.id}
                className="border border-remetra-border rounded-lg p-3.5 bg-remetra-surface"
                onPress={() => handleSelectFood(food)}
              >
                <Text className="text-base font-medium text-neutral-900">{food.name}</Text>
                <Text className="text-xs text-neutral-400 mt-0.5">
                  {food.ingredients.join(", ")}
                </Text>
              </TouchableOpacity>
            ))}
            {searchQuery.trim().length > 0 && (
              <CustomItemButton
                label={`+ Add '${searchQuery}' as custom food`}
                onPress={handleSwitchToCustom}
              />
            )}
          </View>

          {/* Scan barcode button */}
          <TouchableOpacity
            className="border border-remetra-border rounded-full py-3.5 items-center mt-2"
            onPress={() => {
              onCloseModal();
              setTimeout(() => navigation.navigate('BarcodeScanner'), 300);
            }}
          >
            <Text className="text-lg font-ptserif text-remetra-accent">Scan Barcode</Text>
          </TouchableOpacity>
        </>
      )}

      {/* Selected food summary */}
      {selectedFood && !isCustom && (
        <View className="bg-remetra-surface-accent border border-remetra-accent rounded-xl p-3.5 mb-2">
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-neutral-900">{selectedFood.name}</Text>
            <TouchableOpacity onPress={() => { setSelectedFood(null); setSearchQuery(""); }}>
              <Text className="text-sm font-medium font-ptserif text-remetra-accent">Change</Text>
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
            className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface"
            placeholder="Food name"
            value={customName}
            onChangeText={setCustomName}
          />
          {customIngredients.length === 0 && (
            <Text className="text-remetra-muted text-[13px] mb-1">Ingredients</Text>
          )}
          <Chips
            items={customIngredients}
            itemName="Ingredients"
            placeholder="Add Ingredients..."
            onAdd={(ing) => setCustomIngredients((prev) => [...prev, ing])}
            onRemove={(i) => setCustomIngredients((prev) => prev.filter((_, idx) => idx !== i))}
          />
          <TouchableOpacity onPress={() => { setIsCustom(false); setSearchQuery(""); }}>
            <Text className="text-sm font-medium font-ptserif text-remetra-accent mt-2">
              Search bank instead
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Servings + Timestamp */}
      {(selectedFood || isCustom) && (
        <>
          <Text className="text-sm font-semibold font-ptserif text-remetra-accent mt-4 mb-1.5">
            Servings
          </Text>
          <TextInput
            className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface"
            keyboardType="numeric"
            value={servings}
            onChangeText={setServings}
            placeholder="1"
          />

          <Text className="text-sm font-semibold font-ptserif text-remetra-accent mt-4 mb-1.5">
            Time
          </Text>
          <LogDateTimePicker
            value={timestamp}
            onChange={setTimestamp}
            accentColor="#eea487"
          />

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
            <Text className="text-lg font-ptserif text-remetra-accent">Log Food</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};
