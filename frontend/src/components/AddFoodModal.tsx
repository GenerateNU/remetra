import { View, Text, TextInput } from 'react-native';
import { useState } from 'react';
import { useBankStore } from '../store/bankStore';
import { Chips } from './GenericChipComponent';
import { BaseAddModal } from './BaseAddModal';

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

    handleClose()
  };

  const handleClose = () => {
    setFoodName('');
    setIngredients([]);
    setError('');
    onClose();
  };

  return (
    <BaseAddModal visible={visible} onClose={handleClose} onAdd={handleAdd} addLabel="Add Food" error={error}>
      <Text className="text-lg font-light font-ptserif text-remetra-accent">Food Name</Text>
      <TextInput
        value={foodName}
        onChangeText={setFoodName}
        placeholder="e.g. Greek Yogurt, Sourdough Bread"
        placeholderTextColor="#aaa"
        className="border border-remetra-border rounded-lg p-2 mb-4 text-sm"
        style={{ lineHeight: 16}}
      />
      <View className="flex-row justify-between items-baseline">
        <Text className="text-lg font-light font-ptserif text-remetra-accent">Ingredients</Text>
        <Text className="text-xs font-ptserif text-remetra-muted">Press Enter or tap Add</Text>
      </View>
      <Chips
        items={ingredients}
        itemName="Ingredient"
        placeholder="e.g. milk, wheat, soy..."
        onAdd={(ing) => setIngredients((prev) => [...prev, ing])}
        onRemove={(i) => setIngredients((prev) => prev.filter((_, idx) => idx !== i))}
      />
    </BaseAddModal>
  );
}
