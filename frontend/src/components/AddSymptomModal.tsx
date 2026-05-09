import { Text, View } from 'react-native';
import { useState } from 'react';
import { useBankStore } from '../store/bankStore';
import { BaseAddModal } from './BaseAddModal';
import { sensationOptions, locationOptions } from '../types/symptomOptions';
import { ComboBox } from './ComboBox';

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
    setSensation('');
    setLocation('');
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
      <Text className="text-lg font-light font-ptserif text-remetra-espresso/70 mb-1">Sensation</Text>
      <View className="mb-4">
        <ComboBox
          options={sensationOptions}
          value={sensation}
          placeholder="Select a sensation..."
          onSelect={setSensation}
        />
      </View>
      <Text className="text-lg font-light font-ptserif text-remetra-espresso/70 mb-1">Location</Text>
      <View className="mb-4">
        <ComboBox
          options={locationOptions}
          value={location}
          placeholder="Select a location..."
          onSelect={setLocation}
        />
      </View>
    </BaseAddModal>
  );
}
