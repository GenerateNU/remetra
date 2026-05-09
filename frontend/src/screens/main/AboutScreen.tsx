import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, Linking } from 'react-native';
import {
  HeartPlus,
  NotebookPen,
  Search,
  ChartColumn,
  ChevronRight,
  type LucideIcon,
} from 'lucide-react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';

const CONTACT_EMAIL = 'nicole@remetra.tech';

export function AboutScreen() {
  return (
    <View className="flex-1">
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24 }}>
        {/* Hero */}
        <View className="items-center mb-8 mt-2">
          <View className="w-24 h-24 rounded-full bg-remetra-peach justify-center items-center mb-3">
            <HeartPlus size={44} color="#5C2E14" strokeWidth={1.75} />
          </View>
          <Text className="text-2xl font-semibold text-remetra-mauve italic tracking-[2px]">
            REMETRA
          </Text>
          <Text className="text-sm text-remetra-muted mt-2 text-center">
            Est. 2025
          </Text>
        </View>

        {/* Mission */}
        <SectionDivider label="Our Mission" />
        <View className="bg-white/70 rounded-xl p-4 mb-2">
          <Text className="text-[15px] text-neutral-700 leading-6">
            Remetra was founded by Nicole Gaudango after recognizing that many people living with autoimmune and digestive-related conditions 
            lacked a clear way to understand how their lifestyle choices impact their symptoms. She wanted to create a tool 
            that helps users gain peace or mind, feel more in control of their health, and improve their overall quality of life. 
          </Text>
        </View>

        {/* How it works */}
        <SectionDivider label="How It Works" />
        <View className="gap-3">
          <InfoRow Icon={NotebookPen} label="Log meals and symptoms in real time" />
          <InfoRow Icon={ChartColumn} label="Our algorithm uncovers correlations between ingredients and symptoms" />
          <InfoRow Icon={Search} label="Discover hidden patterns and take control of your health" />
        </View>

        {/* Links */}
        <SectionDivider label="Legal" />
        <View className="gap-3">
          <LinkRow label="Privacy Policy" onPress={() => {}} />
          <LinkRow label="Terms of Service" onPress={() => {}} />
        </View>

        {/* Contact */}
        <SectionDivider label="Contact" />
        <TouchableOpacity
          onPress={() => Linking.openURL(`mailto:${CONTACT_EMAIL}`)}
          className="bg-white/70 rounded-xl p-4"
        >
          <Text className="text-xs text-remetra-mauve mb-1 tracking-[1px]">EMAIL</Text>
          <Text selectable className="text-[15px] text-neutral-700">
          {CONTACT_EMAIL}
          </Text>
        </TouchableOpacity>

        {/* Footer */}
        <View className="flex-row items-center justify-around mt-10 mb-4">
          <Text className="text-xs font-semibold text-remetra-surface tracking-[1px]">
            Version {'0.0.0'}
          </Text>
          <Text className="text-xs font-semibold text-remetra-surface tracking-[1px]">
            BUILT BY{' '}
            <Text className="font-bold" style={{ color: '#2563eb' }}>
              GENERATENU
            </Text>
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

function SectionDivider({ label }: { label: string }) {
  return (
    <View className="flex-row items-center mt-4 mb-2">
      <Text className="text-xs text-neutral-600 mr-2 tracking-[1px]">
        {label.toUpperCase()}
      </Text>
      <View className="flex-1 h-px bg-neutral-200" />
    </View>
  );
}

function InfoRow({ Icon, label }: { Icon: LucideIcon; label: string }) {
  return (
    <View className="bg-white/70 rounded-xl p-4 flex-row items-center gap-3">
      <Icon size={20} color="#5C2E14" strokeWidth={2} />
      <Text className="text-[15px] text-neutral-700 flex-1">{label}</Text>
    </View>
  );
}

function LinkRow({ label, onPress }: { label: string; onPress: () => void }) {
  return (
    <TouchableOpacity
      onPress={onPress}
      className="bg-white/70 rounded-xl p-4 flex-row items-center gap-3"
    >
      <Text className="text-[15px] text-neutral-700 flex-1">{label}</Text>
      <ChevronRight size={20} color="#ccc" strokeWidth={2} />
    </TouchableOpacity>
  );
}
