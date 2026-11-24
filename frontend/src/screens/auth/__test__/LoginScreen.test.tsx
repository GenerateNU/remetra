import { ScrollView } from 'react-native';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { LoginScreen } from '../LoginScreen';
import { ApiError } from '../../../api/client';

const mockLogin = jest.fn();
const mockGoBack = jest.fn();

jest.mock('expo-font', () => ({ useFonts: () => [true] }));
jest.mock('@expo-google-fonts/pt-serif', () => ({ PTSerif_400Regular: 0 }));
jest.mock('../../../components/BackgroundGradient', () => ({ BackgroundGradient: () => null }));
jest.mock('../../../navigation/hooks', () => ({
  useAppNavigation: () => ({ goBack: mockGoBack }),
}));
jest.mock('../../../store/useAuthStore', () => ({
  useAuthStore: () => ({ login: mockLogin }),
}));

const fillForm = (username: string, password: string) => {
  fireEvent.changeText(screen.getByPlaceholderText('Username'), username);
  fireEvent.changeText(screen.getByPlaceholderText('Password'), password);
};

describe('LoginScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLogin.mockResolvedValue(undefined);
  });

  describe('password visibility', () => {
    it('masks the password until the eye button is pressed', () => {
      // Arrange
      render(<LoginScreen />);
      const password = () => screen.getByPlaceholderText('Password');
      expect(password().props.secureTextEntry).toBe(true);

      // Act
      fireEvent.press(screen.getByLabelText('Show password'));

      // Assert
      expect(password().props.secureTextEntry).toBe(false);
    });

    it('submits the typed password regardless of visibility', async () => {
      // Arrange
      render(<LoginScreen />);
      fillForm('ashir_1', 'password123');
      fireEvent.press(screen.getByLabelText('Show password'));

      // Act
      fireEvent.press(screen.getByText('Log In'));

      // Assert
      await waitFor(() =>
        expect(mockLogin).toHaveBeenCalledWith({ username: 'ashir_1', password: 'password123' }),
      );
    });
  });

  describe('keyboard handling', () => {
    it('renders the form in a scroll view that keeps the Log In button tappable with the keyboard open', () => {
      // Arrange / Act
      render(<LoginScreen />);

      // Assert
      expect(screen.UNSAFE_getByType(ScrollView).props.keyboardShouldPersistTaps).toBe('handled');
    });
  });

  describe('validation', () => {
    it('shows required errors and does not call login when the form is empty', () => {
      // Arrange
      render(<LoginScreen />);

      // Act
      fireEvent.press(screen.getByText('Log In'));

      // Assert
      expect(screen.getByText('Username is required')).toBeTruthy();
      expect(screen.getByText('Password is required')).toBeTruthy();
      expect(mockLogin).not.toHaveBeenCalled();
    });

    it('rejects passwords shorter than 8 characters', () => {
      // Arrange
      render(<LoginScreen />);
      fillForm('ashir_1', 'short');

      // Act
      fireEvent.press(screen.getByText('Log In'));

      // Assert
      expect(screen.getByText('Password must be at least 8 characters')).toBeTruthy();
      expect(mockLogin).not.toHaveBeenCalled();
    });

    it('clears the password error once the user types again', () => {
      // Arrange
      render(<LoginScreen />);
      fireEvent.press(screen.getByText('Log In'));
      expect(screen.getByText('Password is required')).toBeTruthy();

      // Act
      fireEvent.changeText(screen.getByPlaceholderText('Password'), 'p');

      // Assert
      expect(screen.queryByText('Password is required')).toBeNull();
    });
  });

  describe('server errors', () => {
    it('shows an incorrect-credentials message under the password field', async () => {
      // Arrange
      mockLogin.mockRejectedValue(new ApiError('Incorrect username or password'));
      render(<LoginScreen />);
      fillForm('ashir_1', 'password123');

      // Act
      fireEvent.press(screen.getByText('Log In'));

      // Assert
      expect(await screen.findByText('Incorrect username or password')).toBeTruthy();
    });

    it('shows other API errors as a general message', async () => {
      // Arrange
      mockLogin.mockRejectedValue(new ApiError('Too many attempts'));
      render(<LoginScreen />);
      fillForm('ashir_1', 'password123');

      // Act
      fireEvent.press(screen.getByText('Log In'));

      // Assert
      expect(await screen.findByText('Too many attempts')).toBeTruthy();
    });

    it('shows a fallback message for unexpected errors', async () => {
      // Arrange
      mockLogin.mockRejectedValue(new Error('network down'));
      render(<LoginScreen />);
      fillForm('ashir_1', 'password123');

      // Act
      fireEvent.press(screen.getByText('Log In'));

      // Assert
      expect(await screen.findByText('Something went wrong. Please try again.')).toBeTruthy();
    });
  });

  it('navigates back when Back is pressed', () => {
    // Arrange
    render(<LoginScreen />);

    // Act
    fireEvent.press(screen.getByText('Back'));

    // Assert
    expect(mockGoBack).toHaveBeenCalled();
  });
});
