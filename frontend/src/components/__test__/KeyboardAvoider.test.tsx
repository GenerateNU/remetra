import { Text } from 'react-native';
import { render, screen } from '@testing-library/react-native';
import {
  KeyboardAvoidingView,
  KeyboardAwareScrollView as KCKeyboardAwareScrollView,
} from 'react-native-keyboard-controller';
import { KeyboardAvoider, KeyboardAwareScrollView } from '../KeyboardAvoider';

// react-native-keyboard-controller is mocked in jest.setup.js; the keyboard animation itself is the library's job,
// so these tests check that our wrappers configure it the way the screens rely on.

describe('KeyboardAvoider', () => {
  it('renders its children inside a padding-based KeyboardAvoidingView that fills the space', () => {
    // Arrange / Act
    render(
      <KeyboardAvoider>
        <Text>modal content</Text>
      </KeyboardAvoider>,
    );

    // Assert
    expect(screen.getByText('modal content')).toBeTruthy();
    const avoider = screen.UNSAFE_getByType(KeyboardAvoidingView);
    expect(avoider.props.behavior).toBe('padding');
    expect(avoider.props.style).toEqual([{ flex: 1 }, undefined]);
  });

  it('merges a custom style and passes other props through', () => {
    // Arrange / Act
    render(
      <KeyboardAvoider style={{ backgroundColor: 'white' }} testID="avoider">
        <Text>modal content</Text>
      </KeyboardAvoider>,
    );

    // Assert
    const avoider = screen.UNSAFE_getByType(KeyboardAvoidingView);
    expect(avoider.props.style).toEqual([{ flex: 1 }, { backgroundColor: 'white' }]);
    expect(avoider.props.testID).toBe('avoider');
  });
});

describe('KeyboardAwareScrollView', () => {
  it('renders its children in a scroll view that keeps the focused input visible and lets taps through', () => {
    // Arrange / Act
    render(
      <KeyboardAwareScrollView>
        <Text>form</Text>
      </KeyboardAwareScrollView>,
    );

    // Assert
    expect(screen.getByText('form')).toBeTruthy();
    const scrollView = screen.UNSAFE_getByType(KCKeyboardAwareScrollView);
    expect(scrollView.props.bottomOffset).toBe(24);
    expect(scrollView.props.keyboardShouldPersistTaps).toBe('handled');
    expect(scrollView.props.contentContainerStyle).toEqual({ flexGrow: 1 });
    expect(scrollView.props.bounces).toBe(false);
  });
});
