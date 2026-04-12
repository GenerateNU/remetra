import { View, Text, TouchableOpacity, Modal, TextInput } from 'react-native';
import { useState } from 'react';
import { Dropdown } from 'react-native-element-dropdown';
import { useBankStore } from '../store/bankStore';


interface Props {
  visible: boolean;
  onClose: () => void;
}

const sensationOptions = [
  { label: 'Bloating', value: 'Bloating' },
  { label: 'Cramping', value: 'Cramping' },
  { label: 'Nausea', value: 'Nausea' },
  { label: 'Rash', value: 'Rash' },
  { label: 'Itchiness', value: 'Itchiness' },
  { label: 'Hives', value: 'Hives' },
  { label: 'Headache', value: 'Headache' },
  { label: 'Fatigue', value: 'Fatigue' },
  { label: 'Brain Fog', value: 'Brain Fog' },
  { label: 'Heartburn', value: 'Heartburn' },
  { label: 'Swelling', value: 'Swelling' },
  { label: 'Diarrhea', value: 'Diarrhea' },
  { label: 'Constipation', value: 'Constipation' },
  { label: 'Gas', value: 'Gas' },
  { label: 'Other', value: 'Other' },
];

export function AddSymptomModal({ visible, onClose }: Props) {
  const { addSymptom } = useBankStore();
  const [location, setLocation] = useState('');
  const [sensation, setSensation] = useState('');
  const [error, setError] = useState('');

  const handleAdd = async () => {
    if (!location.trim() || !sensation.trim()) {
      setError('Please fill out all fields.');
      return;
    }
    setError('');
    const name = `${sensation} — ${location}`;
    const id = await addSymptom(name, location, sensation);
    if (!id) {
      setError('Failed to add symptom. Please try again.');
      return;
    }
    setLocation('');
    setSensation('');
  };

  const handleClose = () => {
    setLocation('');
    setSensation('');
    setError('');
    onClose();
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View className="flex-1 bg-black/50 justify-center items-center">
        <View className="bg-white rounded-[20px] p-8 w-4/5">
          <Text className="text-lg font-light font-ptserif text-remetra-accent">Sensation</Text>
          {/* Dropdown is a third-party component that takes a style prop */}
          <Dropdown
            data={sensationOptions}
            search
            labelField="label"
            valueField="value"
            placeholder="Select a sensation..."
            searchPlaceholder="Type to search..."
            value={sensation}
            onChange={item => setSensation(item.value)}
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 16 }}
          />
          <Text className="text-lg font-light font-ptserif text-remetra-accent">Location</Text>
          <TextInput
            value={location}
            onChangeText={setLocation}
            placeholder="e.g. stomach, throat, skin"
            className="border border-remetra-border rounded-lg p-2 mb-4"
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
