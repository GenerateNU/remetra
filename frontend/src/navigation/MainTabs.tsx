import React from 'react';
import { View, Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { TimelineScreen } from '../screens/main/TimelineScreen';
import { AnalysisScreen } from '../screens/main/AnalysisScreen';
import { ProfileScreen } from '../screens/main/ProfileScreen';
import LogEntryModal from '../components/LogEntryModal';
import { useUIStore } from '../store/uiStore';

export type MainTabParamList = {
  History: undefined;
  Analysis: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

function TabIcon({ emoji, focused }: { emoji: string; focused: boolean }) {
  return (
    <View style={{ alignItems: 'center', gap: 2 }}>
      <Text style={{ fontSize: 20 }}>{emoji}</Text>
    </View>
  );
}

export function MainTabs() {
  const { showLogModal, closeLogModal, notifyLogCreated } = useUIStore();

  return (
    <>
      <LogEntryModal
        visible={showLogModal}
        onClose={closeLogModal}
        onLogEntry={() => { notifyLogCreated(); closeLogModal(); }}
      />

      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarShowLabel: false,
          tabBarStyle: {
            backgroundColor: 'white',
            borderTopWidth: 1,
            borderTopColor: '#F0E8E8',
            height: 70,
            paddingBottom: 8,
            paddingTop: 8,
          },
        }}
      >
        <Tab.Screen
          name="History"
          component={TimelineScreen}
          options={{
            tabBarIcon: ({ focused }) => (
              <TabIcon emoji="📋" focused={focused} />
            ),
          }}
        />
        <Tab.Screen
          name="Analysis"
          component={AnalysisScreen}
          options={{
            tabBarIcon: ({ focused }) => (
              <TabIcon emoji="📊"focused={focused} />
            ),
          }}
        />
        <Tab.Screen
          name="Profile"
          component={ProfileScreen}
          options={{
            tabBarIcon: ({ focused }) => (
              <TabIcon emoji="👤" focused={focused} />
            ),
          }}
        />
      </Tab.Navigator>
    </>
  );
}
