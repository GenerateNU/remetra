import { ScrollView } from 'react-native';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { SignupScreen } from '../SignupScreen';
import { ApiError } from '../../../api/client';

const mockRegister = jest.fn();
const mockGoBack = jest.fn();

jest.mock('expo-font', () => ({ useFonts: () => [true] }));
jest.mock('@expo-google-fonts/pt-serif', () => ({ PTSerif_400Regular: 0 }));
jest.mock('../../../components/BackgroundGradient', () => ({ BackgroundGradient: () => null }));
jest.mock('../../../navigation/hooks', () => ({
  useAppNavigation: () => ({ goBack: mockGoBack }),
}));
jest.mock('../../../store/useAuthStore', () => ({
  useAuthStore: () => ({ register: mockRegister }),
}));

const fillForm = (username: string, email: string, password: string) => {
  fireEvent.changeText(screen.getByPlaceholderText('Username'), username);
  fireEvent.changeText(screen.getByPlaceholderText('Email'), email);
  fireEvent.changeText(screen.getByPlaceholderText('Password'), password);
};

describe('SignupScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockRegister.mockResolvedValue(undefined);
    // The screen logs caught errors; keep test output clean.
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('password visibility', () => {
    it('masks the password until the eye button is pressed, then masks it again', () => {
      // Arrange
      render(<SignupScreen />);
      const password = () => screen.getByPlaceholderText('Password');
      expect(password().props.secureTextEntry).toBe(true);

      // Act / Assert
      fireEvent.press(screen.getByLabelText('Show password'));
      expect(password().props.secureTextEntry).toBe(false);

      fireEvent.press(screen.getByLabelText('Hide password'));
      expect(password().props.secureTextEntry).toBe(true);
    });

    it('only toggles the password field, not username or email', () => {
      // Arrange
      render(<SignupScreen />);

      // Act
      fireEvent.press(screen.getByLabelText('Show password'));

      // Assert
      expect(screen.getByPlaceholderText('Username').props.secureTextEntry).toBeFalsy();
      expect(screen.getByPlaceholderText('Email').props.secureTextEntry).toBeFalsy();
    });
  });

  describe('keyboard handling', () => {
    it('renders the form in a scroll view that keeps the Sign Up button tappable with the keyboard open', () => {
      // Arrange / Act
      render(<SignupScreen />);

      // Assert
      expect(screen.UNSAFE_getByType(ScrollView).props.keyboardShouldPersistTaps).toBe('handled');
    });
  });

  describe('validation', () => {
    it('shows required errors for every field and does not call register', () => {
      // Arrange
      render(<SignupScreen />);

      // Act
      fireEvent.press(screen.getByText('Sign Up'));

      // Assert
      expect(screen.getByText('Username is required')).toBeTruthy();
      expect(screen.getByText('Email is required')).toBeTruthy();
      expect(screen.getByText('Password is required')).toBeTruthy();
      expect(mockRegister).not.toHaveBeenCalled();
    });

    it('rejects an invalid email address', () => {
      // Arrange
      render(<SignupScreen />);
      fillForm('ashir_1', 'not-an-email', 'password123');

      // Act
      fireEvent.press(screen.getByText('Sign Up'));

      // Assert
      expect(screen.getByText('Please enter a valid email address')).toBeTruthy();
      expect(mockRegister).not.toHaveBeenCalled();
    });

    it('rejects usernames with special characters', () => {
      // Arrange
      render(<SignupScreen />);
      fillForm('ashir!', 'a@b.com', 'password123');

      // Act
      fireEvent.press(screen.getByText('Sign Up'));

      // Assert
      expect(
        screen.getByText('Username can only contain letters, numbers, and underscores'),
      ).toBeTruthy();
    });
  });

  describe('submitting', () => {
    it('calls register with the form values', async () => {
      // Arrange
      render(<SignupScreen />);
      fillForm('ashir_1', 'a@b.com', 'password123');

      // Act
      fireEvent.press(screen.getByText('Sign Up'));

      // Assert
      await waitFor(() =>
        expect(mockRegister).toHaveBeenCalledWith({
          username: 'ashir_1',
          email: 'a@b.com',
          password: 'password123',
        }),
      );
    });

    it('shows "Username already taken" when the username is registered', async () => {
      // Arrange
      mockRegister.mockRejectedValue(new ApiError('Username already registered'));
      render(<SignupScreen />);
      fillForm('ashir_1', 'a@b.com', 'password123');

      // Act
      fireEvent.press(screen.getByText('Sign Up'));

      // Assert
      expect(await screen.findByText('Username already taken')).toBeTruthy();
    });
  });

  it('navigates back when Back is pressed', () => {
    // Arrange
    render(<SignupScreen />);

    // Act
    fireEvent.press(screen.getByText('Back'));

    // Assert
    expect(mockGoBack).toHaveBeenCalled();
  });
});
