import { View, Text, TouchableOpacity, Modal, TextInput } from 'react-native';
import { useState } from 'react';
import { Dropdown } from 'react-native-element-dropdown';
import { useBankStore } from '../store/bankStore';


interface Props {
  visible: boolean;
  onClose: () => void;
}

export function AddSymptomModal({ visible, onClose }: Props) {
  const { addSymptom } = useBankStore();
  const [symptomName, setSymptomName] = useState('');
  const [symptomLocation, setSymptomLocation] = useState('');
  const [symptomSensation, setSymptomSensation] = useState('');
  const [error, setError] = useState('');

  // More to be added?
  const sensationOptions = [
    { label: 'Rash', value: 'Headache' },
    { label: 'Bloating', value: 'Bloating' },
    { label: 'Itchiness', value: 'Fatigue' },
    { label: 'Cramps', value: 'Cramps' },
  ];

  const handleAdd = () => {
    if (!symptomName.trim() || !symptomLocation.trim() || !symptomSensation.trim()) {
      setError('Please fill out all fields.');
      return;
    }
    setError('');
    addSymptom(symptomName, symptomLocation, symptomSensation);
    setSymptomName('');
    setSymptomLocation('');
    setSymptomSensation('');
  };

  const handleClose = () => {
    setSymptomName('');
    setSymptomLocation('');
    setSymptomSensation('');
    setError('');
    onClose();
  };

  return(
    <Modal visible={visible} transparent animationType="fade">
      <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' }}>
        <View style={{ backgroundColor: 'white', borderRadius: 20, padding: 30, width: '80%' }}>
          <Text className="text-[18px] font-light font-ptserif text-[#eea487]">Enter Symptom Name</Text>
          <TextInput
            value={symptomName}
            onChangeText={setSymptomName}
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 16 }}/>
          <Text className="text-[18px] font-light font-ptserif text-[#eea487]">Enter Symptom Location</Text>
          <TextInput
            value={symptomLocation}
            onChangeText={setSymptomLocation}
            style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 16 }}/>
          <Text className="text-[18px] font-light font-ptserif text-[#eea487]">Choose Symptom Sensation</Text>
          <Dropdown
            data={sensationOptions}
            search
            labelField="label"
            valueField="value"
            placeholder="Search sensations..."
            searchPlaceholder="Type to search..."
            value={symptomSensation}
            onChange={item => setSymptomSensation(item.value)}
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