import { useEffect, useRef, type ReactNode } from 'react';
import { Keyboard, KeyboardAvoidingView, ScrollView, type KeyboardAvoidingViewProps, type ScrollViewInstance } from 'react-native';

// Shrinks its content by the keyboard's height so inputs and buttons near the
// bottom stay visible while typing. Modals render in their own window, so this
// must go *inside* a <Modal>, not around it.
export function KeyboardAvoider({ className, ...props }: KeyboardAvoidingViewProps) {
  return <KeyboardAvoidingView behavior="padding" className={`flex-1 ${className ?? ''}`} {...props} />;
}

// Full-screen version for forms whose inputs sit at the bottom of the content
// (e.g. login/signup): scrolls to the end when the keyboard opens so the fields
// and submit button stay in view. Tapping empty space dismisses the keyboard.
export function KeyboardAwareScrollView({ children }: { children: ReactNode }) {
  const scrollRef = useRef<ScrollViewInstance>(null);

  useEffect(() => {
    const sub = Keyboard.addListener('keyboardDidShow', () => {
      scrollRef.current?.scrollToEnd({ animated: true });
    });
    return () => sub.remove();
  }, []);

  return (
    <KeyboardAvoider>
      <ScrollView
        ref={scrollRef}
        contentContainerStyle={{ flexGrow: 1 }}
        keyboardShouldPersistTaps="handled"
        bounces={false}
      >
        {children}
      </ScrollView>
    </KeyboardAvoider>
  );
}
