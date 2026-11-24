import { Keyboard, KeyboardAvoidingView, ScrollView, Text } from 'react-native';
import { render, screen } from '@testing-library/react-native';
import { KeyboardAvoider, KeyboardAwareScrollView } from '../KeyboardAvoider';

describe('KeyboardAvoider', () => {
  it('renders its children inside a padding-based KeyboardAvoidingView', () => {
    // Arrange / Act
    render(
      <KeyboardAvoider>
        <Text>modal content</Text>
      </KeyboardAvoider>,
    );

    // Assert
    expect(screen.getByText('modal content')).toBeTruthy();
    expect(screen.UNSAFE_getByType(KeyboardAvoidingView).props.behavior).toBe('padding');
  });
});

describe('KeyboardAwareScrollView', () => {
  let keyboardDidShow: (() => void) | undefined;
  // KeyboardAvoidingView registers its own listeners, so track ours separately.
  const removeDidShow = jest.fn();

  beforeEach(() => {
    keyboardDidShow = undefined;
    removeDidShow.mockClear();
    jest.spyOn(Keyboard, 'addListener').mockImplementation((event, handler) => {
      if (event === 'keyboardDidShow') keyboardDidShow = handler as () => void;
      const remove = event === 'keyboardDidShow' ? removeDidShow : jest.fn();
      return { remove } as unknown as ReturnType<typeof Keyboard.addListener>;
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders its children in a scroll view that lets taps through while the keyboard is open', () => {
    // Arrange / Act
    render(
      <KeyboardAwareScrollView>
        <Text>form</Text>
      </KeyboardAwareScrollView>,
    );

    // Assert
    expect(screen.getByText('form')).toBeTruthy();
    expect(screen.UNSAFE_getByType(ScrollView).props.keyboardShouldPersistTaps).toBe('handled');
  });

  it('scrolls to the end when the keyboard opens', () => {
    // Arrange
    const scrollToEnd = jest.spyOn(ScrollView.prototype, 'scrollToEnd').mockImplementation(() => {});
    render(
      <KeyboardAwareScrollView>
        <Text>form</Text>
      </KeyboardAwareScrollView>,
    );

    // Act
    keyboardDidShow?.();

    // Assert
    expect(keyboardDidShow).toBeDefined();
    expect(scrollToEnd).toHaveBeenCalledWith({ animated: true });
  });

  it('removes the keyboard listener on unmount', () => {
    // Arrange
    const { unmount } = render(
      <KeyboardAwareScrollView>
        <Text>form</Text>
      </KeyboardAwareScrollView>,
    );

    // Act
    unmount();

    // Assert
    expect(removeDidShow).toHaveBeenCalledTimes(1);
  });
});
