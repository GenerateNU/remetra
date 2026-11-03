import { Text, TouchableOpacity, View } from 'react-native';
import { useEffect, useState } from 'react';
import { useBankStore } from '../store/bankStore';
import { useUIStore } from '../store/uiStore';
import { symptomLogService } from '../api/symptom_log_service';
import { checkInService } from '../api/check_in_service';
import { BaseAddModal } from './BaseAddModal';
import { sensationOptions, locationOptions } from '../types/symptomOptions';
import { ComboBox } from './ComboBox';

interface Props {
  visible: boolean;
  onClose: () => void;
}

function toLocalDateString(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0')
  return '${year}-${month}-${day}';
}

export function AddSymptomModal({ visible, onClose }: Props) {
  const { addSymptom } = useBankStore();
  const [sensation, setSensation] = useState('');
  const [location, setLocation] = useState('');
  const [error, setError] = useState('');
  const notifyLogCreated = useUIStore((s) => s.notifyLogCreated);
  const logVersion = useUIStore((s) => s.logVersion);
  const [loggedToday, setLoggedToday] = useState(true);
  
  useEffect(() => {
    if (!visible) return;
    const today = toLocalDateString(new Date());
    symptomLogService
      .getMySymptomLogs()
      .then((logs) => setLoggedToday(logs.some((log) => toLocalDateString(new Date(log.timestamp)) === today)))
      .catch(() => setLoggedToday(false));
  }, [visible, logVersion]);

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

  const handleNoSymptoms = async () => {
    try {
      await checkInService.checkInNoSymptoms({
        date: toLocalDateString(new Date()),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      });
      notifyLogCreated();
      handleClose();
    } catch (err: any) {
      setError(err.message ?? 'Failed to record check-in. Please try again.');
    }
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
      {!loggedToday && (
        <TouchableOpacity
          onPress={handleNoSymptoms}
          className="border border-remetra-burgundy rounded-full py-3.5 items-center"
          >
            <Text className="text-base font-ptserif text-remetra-burgundy">No symptoms today</Text>
        </TouchableOpacity>
      )}
    </BaseAddModal>
  );
}
