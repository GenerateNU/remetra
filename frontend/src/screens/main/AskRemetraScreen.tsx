import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView, Text, View } from 'react-native';
import type { ScrollViewInstance } from 'react-native';
import { RouteProp, useRoute } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { DawnWash } from '../../components/DawnWash';
import LogEntryModal from '../../components/LogEntryModal';
import type { FoodPrefill } from '../../components/FoodLogForm';
import { AskStart } from '../../components/ask/AskStart';
import { AskToast } from '../../components/ask/AskToast';
import { AskTopBar } from '../../components/ask/AskTopBar';
import { Attachment, AssistantBubble, TypingBubble, UserBubble } from '../../components/ask/ChatBubble';
import { Composer } from '../../components/ask/Composer';
import { SuggestionChips } from '../../components/ask/SuggestionChips';
import { ThreadMarkerRow } from '../../components/ask/ThreadMarkerRow';
import { ChatCardView } from '../../components/ask/cards/ChatCardView';
import { useAskFonts } from '../../components/ask/useAskFonts';
import { useAppNavigation } from '../../navigation/hooks';
import { CHAT_USES_MOCK } from '../../api/chat_service';
import type { MainStackParamList } from '../../navigation/stacks/MainStack';
import { useAuthStore } from '../../store/useAuthStore';
import { ASK_MARKERS, ingredientsFrom, useChatStore } from '../../store/useChatStore';
import type { ThreadItem } from '../../types/chat';

const TOP_BAR_HEIGHT = 62;

export function AskRemetraScreen() {
  const navigation = useAppNavigation();
  const entry = useRoute<RouteProp<MainStackParamList, 'AskRemetra'>>().params?.entry;
  const insets = useSafeAreaInsets();
  const fontsReady = useAskFonts();
  const name = useAuthStore((state) => state.user.name);

  const items = useChatStore((state) => state.items);
  const isReplying = useChatStore((state) => state.isReplying);
  const toast = useChatStore((state) => state.toast);
  const start = useChatStore((state) => state.start);
  const send = useChatStore((state) => state.send);
  const markDraftSaved = useChatStore((state) => state.markDraftSaved);
  const dismissToast = useChatStore((state) => state.dismissToast);

  const scrollRef = useRef<ScrollViewInstance>(null);
  const [editing, setEditing] = useState<{ id: string; prefill: FoodPrefill } | null>(null);

  useEffect(() => {
    start(entry);
  }, [entry, start]);

  const editDraft = useCallback(
    (id: string) => {
      const item = items.find((candidate) => candidate.id === id);
      if (item?.type !== 'card' || item.card.type !== 'draft_food') return;
      const { food, loggedAt } = item.card;
      setEditing({ id, prefill: { name: food, ingredients: ingredientsFrom(food), timestamp: new Date(loggedAt) } });
    },
    [items]
  );

  const isStart = items.length === 0;
  const inLogContext =
    CHAT_USES_MOCK &&
    (entry === 'log' || items.some((item) => item.type === 'marker' && item.marker.label === ASK_MARKERS.log.label));

  const renderItem = (item: ThreadItem) => {
    switch (item.type) {
      case 'marker':
        return <ThreadMarkerRow key={item.id} marker={item.marker} />;
      case 'user':
        return <UserBubble key={item.id} text={item.text} />;
      case 'text':
        return <AssistantBubble key={item.id} text={item.text} />;
      case 'card':
        return (
          <Attachment key={item.id}>
            <ChatCardView item={item} onEditDraft={editDraft} />
          </Attachment>
        );
      case 'suggestions':
        return (
          <Attachment key={item.id}>
            <SuggestionChips items={item.items} onSelect={(text) => void send(text)} disabled={isReplying} />
          </Attachment>
        );
    }
  };

  if (!fontsReady) {
    return (
      <View className="flex-1 items-center justify-center bg-remetra-sheet">
        <ActivityIndicator color="#b5582f" />
      </View>
    );
  }

  return (
    <View className="flex-1 bg-remetra-sheet">
      <DawnWash />
      <KeyboardAvoidingView
        className="flex-1"
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={{ paddingTop: insets.top }}
      >
        <AskTopBar title="Ask Remetra" onBack={() => navigation.goBack()} />
        <ScrollView
          ref={scrollRef}
          className="flex-1"
          contentContainerStyle={{
            flexGrow: 1,
            justifyContent: isStart ? 'center' : 'flex-end',
            gap: isStart ? 18 : 14,
            paddingHorizontal: 16,
            paddingTop: 20,
            paddingBottom: 12,
          }}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode="interactive"
          onContentSizeChange={() => !isStart && scrollRef.current?.scrollToEnd({ animated: true })}
        >
          {isStart ? (
            <AskStart name={name} onSend={(text, marker) => void send(text, marker)} disabled={isReplying} />
          ) : (
            items.map(renderItem)
          )}
          {isReplying && <TypingBubble />}
        </ScrollView>
        <Text className="mt-3 px-6 text-center font-figtree text-[12px] leading-4 text-remetra-text-tertiary">
          Answers use only your own logs. For medical questions, talk to your clinician.
        </Text>
        <View className="mx-4 mt-[27px]" style={{ marginBottom: Math.max(insets.bottom, 12) + 6 }}>
          <Composer
            placeholder={inLogContext ? 'Tell me what you ate or how you feel' : 'Ask about your symptoms or meals'}
            disabled={isReplying}
            onSend={(text) => void send(text)}
          />
        </View>
      </KeyboardAvoidingView>

      {toast && (
        <AskToast
          key={toast.id}
          message={toast.message}
          top={insets.top + TOP_BAR_HEIGHT + 8}
          onDismiss={dismissToast}
        />
      )}

      <LogEntryModal
        visible={editing !== null}
        initialStep="food"
        foodPrefill={editing?.prefill}
        onClose={() => setEditing(null)}
        onLogEntry={(logged) => {
          if (editing && logged.type === 'food') markDraftSaved(editing.id, logged.name, logged.timestamp);
        }}
      />
    </View>
  );
}
