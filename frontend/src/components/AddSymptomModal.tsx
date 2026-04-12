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
      <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' }}>
        <View style={{ backgroundColor: 'white', borderRadius: 20, padding: 30, width: '80%' }}>
          <Text className="text-[18px] font-light font-ptserif text-[#eea487]">Sensation</Text>
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
          <Text className="text-[18px] font-light font-ptserif text-[#eea487]">Location</Text>
          <TextInput
            value={location}
            onChangeText={setLocation}
            placeholder="e.g. stomach, throat, skin"
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 16 }}
          />
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
