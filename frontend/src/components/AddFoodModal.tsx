import { View, Text, TouchableOpacity, Modal, TextInput } from 'react-native';
import { useState } from 'react';
import { useBankStore } from '../store/bankStore';

interface Props {
  visible: boolean;
  onClose: () => void;
}

export function AddFoodModal({ visible, onClose }: Props) {
  const { addFood } = useBankStore();
  const [foodName, setFoodName] = useState('');
  const [foodIngredients, setFoodIngredients] = useState('');
  const [error, setError] = useState('');

  const handleAdd = () => {
    if (!foodName.trim() || !foodIngredients.trim()) {
      setError('Please fill out all fields.');
      return;
    }
    setError('');
    // This needs a big change - we are not accepting one string as an ingredient
    addFood(foodName, [foodIngredients]);
    setFoodName('');
    setFoodIngredients('');
  };

  const handleClose = () => {
    setFoodName('');
    setFoodIngredients('');
    setError('');
    onClose();
  };

  return(
    <Modal visible={visible} transparent animationType="fade">
      <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' }}>
        <View style={{ backgroundColor: 'white', borderRadius: 20, padding: 30, width: '80%' }}>
          <Text className="text-[18px] font-light font-ptserif text-[#eea487]">Enter Food Name</Text>
          <TextInput
            value={foodName}
            onChangeText={setFoodName}
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 16 }}/>
          <Text className="text-[18px] font-light font-ptserif text-[#eea487]">Enter Ingredients</Text>
          <TextInput
            value={foodIngredients}
            onChangeText={setFoodIngredients}
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 16 }}/>
          {error ? <Text style={{ color: 'red', marginBottom: 8 }}>{error}</Text> : null}
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 16 }}>
            <TouchableOpacity onPress={handleAdd}
              style={{
                borderWidth: 1,
                borderColor: '#ccc',
                borderRadius: 25,
                paddingVertical: 10,
                paddingHorizontal: 10,
              }}>
              <Text className="text-[16px] font-light font-ptserif text-[#eea487]">Add</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={handleClose}
                style={{
                  borderWidth: 1,
                  borderColor: '#ccc',
                  borderRadius: 25,
                  paddingVertical: 10,
                  paddingHorizontal: 10,
                }}>
                <Text className="text-[16px] font-light font-ptserif text-[#eea487]">Cancel</Text>
            </TouchableOpacity>
            </View>
        </View>
      </View>
    </Modal>
  );
}