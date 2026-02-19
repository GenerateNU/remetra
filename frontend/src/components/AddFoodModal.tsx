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

  const handleAdd = () => {
    if (!foodName.trim()) {
      setError('Please enter a food name.');
      return;
    }
    setError('');
    addFood(foodName, ingredients);
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
      <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' }}>
        <View style={{ backgroundColor: 'white', borderRadius: 20, padding: 30, width: '80%' }}>
          <Text className="text-[18px] font-light font-ptserif text-[#eea487]">Food Name</Text>
          <TextInput
            value={foodName}
            onChangeText={setFoodName}
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 16 }}
          />

          <Text className="text-[18px] font-light font-ptserif text-[#eea487] mt-4">Ingredients</Text>
          <Chips
            items={ingredients}
            itemName="Ingredient"
            onAdd={(ing) => setIngredients((prev) => [...prev, ing])}
            onRemove={(i) => setIngredients((prev) => prev.filter((_, idx) => idx !== i))}
          />

          {error ? <Text style={{ color: 'red', marginBottom: 8 }}>{error}</Text> : null}

          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 16 }}>
            <TouchableOpacity
              onPress={handleAdd}
              style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 25, paddingVertical: 10, paddingHorizontal: 10 }}
            >
              <Text className="text-[16px] font-light font-ptserif text-[#eea487]">Add</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={handleClose}
              style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 25, paddingVertical: 10, paddingHorizontal: 10 }}
            >
              <Text className="text-[16px] font-light font-ptserif text-[#eea487]">Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}