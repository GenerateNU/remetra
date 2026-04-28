import { FoodLogEntry, FoodItem } from "../types/logs";
import { useBankStore } from "../store/bankStore";
import { Chips } from "./GenericChipComponent";
import { foodLogService } from "../api/food_log_service";
import { useAuthStore } from "../store/useAuthStore";
import { useNavigation } from '@react-navigation/native';
import { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, TextInput } from "react-native";
import { LogDateTimePicker } from "./LogDateTimePicker";

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
      <TouchableOpacity onPress={() => {
        if (!selectedFood && !isCustom) {
          onBack()
        } else {
          setIsCustom(false); setSearchQuery(""); setSelectedFood(null)
        }
        }}>
        <Text className="text-base font-ptserif text-remetra-burgundy mb-4">← Back</Text>
      </TouchableOpacity>
      <View className="flex-row justify-between items-center mb-3">
        <Text className="text-2xl font-bold font-ptserif text-remetra-espresso">
          Log Food
        </Text>
        {!selectedFood && !isCustom && (
          <TouchableOpacity
            className="border border-remetra-burgundy/80 bg-remetra-burgundy/80 rounded-full py-1 px-2"
            onPress={() => {
              onCloseModal();
              setTimeout(() => navigation.navigate('BarcodeScanner'), 300);
            }}
          >
            <Text className="text-s font-ptserif text-white">Scan Barcode</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Search / Select */}
      {!selectedFood && !isCustom && (
        <>
          <TextInput
            className="border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface"
            placeholder="Search foods..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <TouchableOpacity
            className="rounded-lg p-3.5 bg-remetra-burgundy mb-2 opacity-80"
            onPress={handleSwitchToCustom}
            activeOpacity={0.6}
          >
            <Text className="font-medium text-base font-ptserif text-white">+ New Food</Text>
          </TouchableOpacity>

          <View className="gap-2 mb-3">
            {filtered.map((food) => (
              <TouchableOpacity
                key={food.id}
                className="border border-remetra-mauve/40 rounded-lg p-3.5 bg-remetra-surface/30"
                onPress={() => handleSelectFood(food)}
              >
                <Text className="text-base font-medium text-remetra-espresso">{food.name}</Text>
                <Text className="text-xs text-remetra-burgundy mt-0.5">
                  {food.ingredients.join(", ")}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </>
      )}

      {/* Selected food summary */}
      {selectedFood && !isCustom && (
        <View className="bg-remetra-surface-accent border border-remetra-espresso/80 rounded-xl p-3.5 mb-2">
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-remetra-espresso">{selectedFood.name}</Text>
          </View>
          <Text className="text-xs text-remetra-warm-brown mt-0.5">
            {selectedFood.ingredients.join(", ")}
          </Text>
        </View>
      )}

      {/* Custom food entry */}
      {isCustom && (
        <View>
          <TextInput
            className="text-sm border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface text-remetra-espresso"
            placeholder="Food name"
            value={customName}
            onChangeText={setCustomName}
          />
          <View className="flex-row justify-between items-center">
            <Text className="text-sm font-ptserif text-remetra-warm-brown mt-2 mb-1">Ingredients</Text>
            <Text className="text-xs font-ptserif text-remetra-muted mt-2 mb-1">Enter to Add</Text>
          </View>
          <Chips
            items={customIngredients}
            itemName="Ingredients"
            placeholder="Add Ingredients..."
            chipClassName='bg-remetra-burgundy/80'
            chipTextClassName='text-white'
            removeTextClassName='text-white'
            onAdd={(ing) => setCustomIngredients((prev) => [...prev, ing])}
            onRemove={(i) => setCustomIngredients((prev) => prev.filter((_, idx) => idx !== i))}
          />
        </View>
      )}

      {/* Servings + Timestamp */}
      {(selectedFood || isCustom) && (
        <>
          <Text className="text-sm font-ptserif text-remetra-warm-brown mt-4 mb-1.5">
            Servings
          </Text>
          <TextInput
            className="text-sm border border-remetra-border rounded-lg p-3 bg-remetra-surface text-remetra-espresso"
            value={servings}
            onChangeText={setServings}
            placeholder="e.g. '1 cup', '2 slices'"
          />

          <Text className="text-sm font-semibold font-ptserif text-remetra-espresso mt-4 mb-1.5">
            Time
          </Text>
          <LogDateTimePicker
            value={timestamp}
            onChange={setTimestamp}
            accentColor="#b8624fc0"
          />

          <Text className="text-sm font-semibold font-ptserif text-remetra-warm-brown mt-4 mb-1.5">
            Notes (optional)
          </Text>
          <TextInput
            className="text-sm border border-remetra-border rounded-lg p-3 mb-2 bg-remetra-surface text-remetra-espresso"
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
            <Text className="text-lg font-ptserif text-white">Log Food</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};
