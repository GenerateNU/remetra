/**
 * LogDateTimePicker
 *
 * A consistent date+time picker used across log creation and editing.
 *
 * iOS:  tapping the button reveals an inline spinner that stays open.
 *       A "Done" bar confirms the selection.
 * Android: tapping opens the native date dialog followed by the time dialog.
 */

import React, { useState } from 'react';
import { Modal, Platform, Text, TouchableOpacity, View } from 'react-native';
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';

interface LogDateTimePickerProps {
  value: Date;
  onChange: (date: Date) => void;
  /** Defaults to now (can't log in the future) */
  maximumDate?: Date;
  /** Tint colour for the trigger button label and Done bar */
  accentColor?: string;
}

function pad(n: number) {
  return String(n).padStart(2, '0');
}

function formatDisplay(date: Date): string {
  const weekday = date.toLocaleDateString([], { weekday: 'short' });
  const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
  const h = date.getHours();
  const m = pad(date.getMinutes());
  const ampm = h >= 12 ? 'PM' : 'AM';
  const h12 = h % 12 === 0 ? 12 : h % 12;
  return `${weekday}, ${dateStr}  ·  ${h12}:${m} ${ampm}`;
}

// ─── iOS inline picker ────────────────────────────────────────────────────────

function IOSPicker({
  value,
  maximumDate,
  onDone,
  onCancel,
  accentColor,
}: {
  value: Date;
  maximumDate: Date;
  onDone: (date: Date) => void;
  onCancel: () => void;
  accentColor: string;
}) {
  // Keep a local draft so the spinner doesn't commit on every scroll tick
  const [draft, setDraft] = useState(value);

  return (
    <Modal transparent animationType="slide">
      <View style={{ flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.35)' }}>
        {/* Header bar */}
        <View
          style={{
            flexDirection: 'row',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: 'white',
            paddingHorizontal: 20,
            paddingVertical: 12,
            borderTopLeftRadius: 16,
            borderTopRightRadius: 16,
            borderBottomWidth: 1,
            borderBottomColor: '#F0E8E8',
          }}
        >
          <TouchableOpacity onPress={onCancel} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
            <Text style={{ fontSize: 16, color: '#999' }}>Cancel</Text>
          </TouchableOpacity>
          <Text style={{ fontSize: 15, fontWeight: '600', color: '#555' }}>Select Date & Time</Text>
          <TouchableOpacity onPress={() => onDone(draft)} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
            <Text style={{ fontSize: 16, fontWeight: '700', color: accentColor }}>Done</Text>
          </TouchableOpacity>
        </View>

        {/* Spinner */}
        <View style={{ backgroundColor: 'white', paddingBottom: 32 }}>
          <DateTimePicker
            value={draft}
            mode="datetime"
            display="spinner"
            maximumDate={maximumDate}
            onChange={(_: DateTimePickerEvent, selected?: Date) => {
              if (selected) setDraft(selected);
            }}
            style={{ height: 200 }}
          />
        </View>
      </View>
    </Modal>
  );
}

// ─── Android two-step picker ──────────────────────────────────────────────────

function AndroidPicker({
  value,
  maximumDate,
  onDone,
  onCancel,
}: {
  value: Date;
  maximumDate: Date;
  onDone: (date: Date) => void;
  onCancel: () => void;
}) {
  const [step, setStep] = useState<'date' | 'time'>('date');
  const [dateDraft, setDateDraft] = useState(value);

  const handleDateChange = (_: DateTimePickerEvent, selected?: Date) => {
    if (!selected) { onCancel(); return; }
    setDateDraft(selected);
    setStep('time');
  };

  const handleTimeChange = (_: DateTimePickerEvent, selected?: Date) => {
    if (!selected) { onCancel(); return; }
    // Combine the picked date with the picked time
    const combined = new Date(dateDraft);
    combined.setHours(selected.getHours(), selected.getMinutes(), 0, 0);
    onDone(combined);
  };

  if (step === 'date') {
    return (
      <DateTimePicker
        value={dateDraft}
        mode="date"
        display="default"
        maximumDate={maximumDate}
        onChange={handleDateChange}
      />
    );
  }

  return (
    <DateTimePicker
      value={dateDraft}
      mode="time"
      display="default"
      onChange={handleTimeChange}
    />
  );
}

// ─── public component ─────────────────────────────────────────────────────────

export function LogDateTimePicker({
  value,
  onChange,
  maximumDate,
  accentColor = '#B8624F',
}: LogDateTimePickerProps) {
  const [open, setOpen] = useState(false);
  const maxDate = maximumDate ?? (() => { const d = new Date(); d.setHours(23, 59, 59, 999); return d; })();

  const handleDone = (date: Date) => {
    onChange(date);
    setOpen(false);
  };

  const handleCancel = () => setOpen(false);

  return (
    <>
      <TouchableOpacity
        onPress={() => setOpen(true)}
        activeOpacity={0.7}
        style={{
          flexDirection: 'row',
          alignItems: 'center',
          borderWidth: 1,
          borderColor: '#ddd',
          borderRadius: 10,
          paddingHorizontal: 14,
          paddingVertical: 12,
          backgroundColor: '#fafafa',
          gap: 10,
        }}
      >
        <Text style={{ fontSize: 15, color: '#333', flex: 1 }}>{formatDisplay(value)}</Text>
        <Text style={{ fontSize: 12, color: accentColor, fontWeight: '600' }}>Change</Text>
      </TouchableOpacity>

      {open && Platform.OS === 'ios' && (
        <IOSPicker
          value={value}
          maximumDate={maxDate}
          onDone={handleDone}
          onCancel={handleCancel}
          accentColor={accentColor}
        />
      )}

      {open && Platform.OS === 'android' && (
        <AndroidPicker
          value={value}
          maximumDate={maxDate}
          onDone={handleDone}
          onCancel={handleCancel}
        />
      )}
    </>
  );
}
