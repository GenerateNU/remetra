import type { ReactNode } from 'react';
import {
  KeyboardAvoidingView,
  KeyboardAwareScrollView as KCKeyboardAwareScrollView,
  type KeyboardAvoidingViewProps,
} from 'react-native-keyboard-controller';

// Shrinks its content by the keyboard's height, frame-by-frame with the keyboard
// animation, so inputs and buttons near the bottom stay visible while typing.
// Modals render in their own window, so this must go *inside* a <Modal>.
// Uses `style`, not `className`: NativeWind doesn't map classes onto
// third-party components unless they're registered with cssInterop.
export function KeyboardAvoider({ style, ...props }: KeyboardAvoidingViewProps) {
  return <KeyboardAvoidingView behavior="padding" style={[{ flex: 1 }, style]} {...props} />;
}

// Full-screen scrolling form (e.g. login/signup): scrolls just enough to keep
// the *focused* input visible above the keyboard. Tapping empty space dismisses
// the keyboard.
export function KeyboardAwareScrollView({ children }: { children: ReactNode }) {
  return (
    <KCKeyboardAwareScrollView
      bottomOffset={24}
      contentContainerStyle={{ flexGrow: 1 }}
      keyboardShouldPersistTaps="handled"
      bounces={false}
    >
      {children}
    </KCKeyboardAwareScrollView>
  );
}
