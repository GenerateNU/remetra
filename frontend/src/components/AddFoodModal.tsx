import { View, Text, TouchableOpacity, Modal, TextInput } from 'react-native';
import { useState } from 'react';
import { useBankStore } from '../store/bankStore';
import { Chips } from './GenericChipComponent';

interface Props {
  visible: boolean;
  onClose: () => void;
}

export function AddFoodModal({ visible, onClose }: Props) {
  const { addFood } = useBankStore();
  const [foodName, setFoodName] = useState('');
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [error, setError] = useState('');

  const handleAdd = async () => {
    if (!foodName.trim()) {
      setError('Please enter a food name.');
      return;
    }

    setError('');
    const id = await addFood(foodName, ingredients);
    if (!id) {
      setError('Failed to add food. Please try again.');
      return;
    }

    setFoodName('');
    setIngredients([]);
  };

  const handleClose = () => {
    setFoodName('');
    setIngredients([]);
    setError('');
    onClose();
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View className="flex-1 bg-black/50 justify-center items-center">
        <View className="bg-white rounded-[20px] p-8 w-4/5">
          <Text className="text-lg font-light font-ptserif text-remetra-accent">Food Name</Text>
          <TextInput
            value={foodName}
            onChangeText={setFoodName}
            className="border border-remetra-border rounded-lg p-2 mb-4"
          />

          <Text className="text-lg font-light font-ptserif text-remetra-accent mt-4">Ingredients</Text>
          <Chips
            items={ingredients}
            itemName="Ingredient"
            onAdd={(ing) => setIngredients((prev) => [...prev, ing])}
            onRemove={(i) => setIngredients((prev) => prev.filter((_, idx) => idx !== i))}
          />

          {error ? <Text className="text-red-500 mb-2">{error}</Text> : null}

          <View className="flex-row justify-between mt-4">
            <TouchableOpacity
              onPress={handleAdd}
              className="border border-remetra-border rounded-full py-2.5 px-2.5"
            >
              <Text className="text-base font-light font-ptserif text-remetra-accent">Add</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={handleClose}
              className="border border-remetra-border rounded-full py-2.5 px-2.5"
            >
              <Text className="text-base font-light font-ptserif text-remetra-accent">Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}
