import { Text } from 'react-native';
import { useState } from 'react';
import { Dropdown } from 'react-native-element-dropdown';
import { useBankStore } from '../store/bankStore';
import { BaseAddModal } from './BaseAddModal';
import { sensationOptions, locationOptions } from '../types/symptomOptions';

interface Props {
  visible: boolean;
  onClose: () => void;
}

export function AddSymptomModal({ visible, onClose }: Props) {
  const { addSymptom } = useBankStore();
  const [sensation, setSensation] = useState('');
  const [location, setLocation] = useState('');
  const [error, setError] = useState('');

  const handleAdd = async () => {
    if (!sensation || !location) {
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
    handleClose()

  };

  const handleClose = () => {
    setSensation('');
    setLocation('');
    setError('');
    onClose();
  };

  return (
    <BaseAddModal visible={visible} onClose={handleClose} onAdd={handleAdd} addLabel="Add Symptom" error={error}>
      <Text className="text-lg font-light font-ptserif text-remetra-accent">Sensation</Text>
      {/* Dropdown is a third-party component that only accepts style, not className */}
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
        placeholderStyle={{ color: '#aaa', fontSize: 14 }}
        selectedTextStyle={{ fontSize: 14 }}
      />
      <Text className="text-lg font-light font-ptserif text-remetra-accent">Location</Text>
      {/* Dropdown is a third-party component that only accepts style, not className */}
      <Dropdown
        data={locationOptions}
        search
        labelField="label"
        valueField="value"
        placeholder="Select a location..."
        searchPlaceholder="Type to search..."
        value={location}
        onChange={item => setLocation(item.value)}
        style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 16 }}
        placeholderStyle={{ color: '#aaa', fontSize: 14 }}
        selectedTextStyle={{ fontSize: 14 }}
      />
    </BaseAddModal>
  );
}
