import React, { useEffect, useRef } from 'react';
import { View, Platform } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { TimelineScreen } from '../screens/main/TimelineScreen';
import { AnalysisScreen } from '../screens/main/AnalysisScreen';
import { ProfileScreen } from '../screens/main/ProfileScreen';
import LogEntryModal from '../components/LogEntryModal';
import { useUIStore } from '../store/uiStore';
import { ClipboardList, ChartColumn, User, type LucideIcon } from 'lucide-react-native';
import * as Notifications from "expo-notifications";

export type MainTabParamList = {
  History: undefined;
  Analysis: undefined;
  Profile: undefined;
};

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowBanner: true,
    shouldShowList: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

const Tab = createBottomTabNavigator<MainTabParamList>();

const TAB_ACTIVE_COLOR = '#B8624F';
const TAB_INACTIVE_COLOR = '#b2939b';

function TabIcon({ Icon, focused }: { Icon: LucideIcon; focused: boolean }) {
  return (
    <View style={{ alignItems: 'center', gap: 2 }}>
      <Icon size={24} color={focused ? TAB_ACTIVE_COLOR : TAB_INACTIVE_COLOR} strokeWidth={focused ? 2.25 : 2} />
    </View>
  );
}

export function MainTabs() {
  const { showLogModal, closeLogModal, initialLogType } = useUIStore();
  const lastResponse = Notifications.useLastNotificationResponse();
  const handledId = useRef<string | null>(null);

  useEffect(() => {
    (async () => {
      if (Platform.OS === 'android') { // added android support bc of my windows laptop i need android emulator
        await Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.DEFAULT,
        });
      }
      await Notifications.requestPermissionsAsync();
    })();
  }, []);

  useEffect(() => {
    if (!lastResponse) return;
    const id = lastResponse.notification.request.identifier;
    if (handledId.current === id) return;
    if (lastResponse.notification.request.content.data?.log_type === 'symptom') {
      handledId.current = id;
      useUIStore.getState().openLogModal('symptom');
    }
  }, [lastResponse]);

  return (
    <>
      <LogEntryModal
        visible={showLogModal}
        onClose={closeLogModal}
        onLogEntry={closeLogModal}
        initialStep={initialLogType ?? 'select_type'}
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
              <TabIcon Icon={ClipboardList} focused={focused} />
            ),
          }}
        />
        <Tab.Screen
          name="Analysis"
          component={AnalysisScreen}
          options={{
            tabBarIcon: ({ focused }) => (
              <TabIcon Icon={ChartColumn} focused={focused} />
            ),
          }}
        />
        <Tab.Screen
          name="Profile"
          component={ProfileScreen}
          options={{
            tabBarIcon: ({ focused }) => (
              <TabIcon Icon={User} focused={focused} />
            ),
          }}
        />
      </Tab.Navigator>
    </>
  );
}
